import re
from dataclasses import asdict, dataclass, field
from typing import List, Optional

import dns.exception
import dns.resolver

EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@'
    r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
)

ROLE_LOCAL_PARTS = {
    'admin', 'billing', 'contact', 'hello', 'help', 'hr', 'info',
    'jobs', 'mailer-daemon', 'marketing', 'noreply', 'no-reply',
    'postmaster', 'recruiting', 'sales', 'security', 'support',
    'webmaster',
}

FREE_EMAIL_DOMAINS = {
    'aol.com', 'gmail.com', 'googlemail.com', 'hotmail.com', 'icloud.com',
    'live.com', 'mail.com', 'msn.com', 'outlook.com', 'proton.me',
    'protonmail.com', 'yahoo.com', 'ymail.com', 'zoho.com',
}

DISPOSABLE_DOMAINS = {
    '10minutemail.com', 'dispostable.com', 'guerrillamail.com',
    'mailinator.com', 'sharklasers.com', 'temp-mail.org', 'tempmail.com',
    'throwaway.email', 'trashmail.com', 'yopmail.com',
}

DNS_TIMEOUT_SECONDS = 3


@dataclass
class DomainChecks:
    domain: str
    format_valid: bool = True
    a_records: List[str] = field(default_factory=list)
    mx_records: List[str] = field(default_factory=list)
    has_spf: bool = False
    has_dmarc: bool = False
    dns_error: Optional[str] = None


@dataclass
class EmailChecks:
    email: str
    local_part: str = ''
    domain: str = ''
    format_valid: bool = False
    domain_checks: Optional[DomainChecks] = None
    disposable_domain: bool = False
    free_email_provider: bool = False
    role_account: bool = False


def _is_disposable_domain(domain: str) -> bool:
    if domain in DISPOSABLE_DOMAINS:
        return True
    return any(domain.endswith(f'.{disposable}') for disposable in DISPOSABLE_DOMAINS)


def _query_records(domain: str, record_type: str) -> List[str]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    try:
        answers = resolver.resolve(domain, record_type)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        return []
    except dns.resolver.NoNameservers:
        return []
    except Exception:
        return []

    values = []
    for answer in answers:
        if record_type == 'MX':
            values.append(str(answer.exchange).rstrip('.'))
        elif record_type in ('A', 'AAAA'):
            values.append(str(answer))
        elif record_type == 'TXT':
            values.append(str(answer).strip('"'))
    return values


def validate_domain(domain: str) -> dict:
    normalized = domain.strip().lower().rstrip('.')
    checks = DomainChecks(domain=normalized, format_valid=bool(normalized and '.' in normalized))

    if '@' in normalized:
        checks.format_valid = False

    if not checks.format_valid:
        return _build_domain_result(checks)

    try:
        checks.a_records = _query_records(normalized, 'A') + _query_records(normalized, 'AAAA')
        checks.mx_records = _query_records(normalized, 'MX')
        txt_records = _query_records(normalized, 'TXT')
        joined_txt = ' '.join(txt_records).lower()
        checks.has_spf = 'v=spf1' in joined_txt
        checks.has_dmarc = _query_records(f'_dmarc.{normalized}', 'TXT') != []
    except Exception as exc:
        checks.dns_error = str(exc)

    return _build_domain_result(checks)


def validate_email(email: str) -> dict:
    normalized = email.strip().lower()
    local_part, _, domain = normalized.partition('@')
    checks = EmailChecks(
        email=normalized,
        local_part=local_part,
        domain=domain,
        format_valid=bool(EMAIL_PATTERN.match(normalized)),
    )

    if not checks.format_valid:
        return _build_email_result(checks)

    domain_result = validate_domain(domain)
    checks.disposable_domain = _is_disposable_domain(domain)
    checks.free_email_provider = domain in FREE_EMAIL_DOMAINS
    checks.role_account = local_part in ROLE_LOCAL_PARTS
    checks.domain_checks = DomainChecks(**domain_result['checks'])

    return _build_email_result(checks, domain_result=domain_result)


def _build_domain_result(checks: DomainChecks) -> dict:
    score = 0
    signals = []

    if not checks.format_valid:
        score = 0
        signals.append('Invalid domain format')
    else:
        score = 20
        if checks.a_records:
            score += 20
            signals.append('Domain resolves (A/AAAA records found)')
        else:
            signals.append('Domain does not resolve to an IP address')

        if checks.mx_records:
            score += 35
            signals.append('Mail exchange (MX) records found')
        else:
            score -= 15
            signals.append('No MX records — domain may not receive email')

        if checks.has_spf:
            score += 10
            signals.append('SPF record present')

        if checks.has_dmarc:
            score += 15
            signals.append('DMARC record present')

    score = max(0, min(100, score))
    likely_legit = score >= 60 and bool(checks.mx_records or checks.a_records)

    return {
        'input_type': 'domain',
        'input_value': checks.domain,
        'score': score,
        'is_likely_legit': likely_legit,
        'recommendation': _recommendation(score, checks.mx_records, disposable=False),
        'checks': asdict(checks),
        'signals': signals,
    }


def _build_email_result(checks: EmailChecks, domain_result=None) -> dict:
    domain_checks = checks.domain_checks or DomainChecks(domain=checks.domain)
    score = domain_result['score'] if domain_result else 0
    signals = list(domain_result['signals']) if domain_result else []

    if not checks.format_valid:
        score = 0
        signals = ['Invalid email format']
    else:
        if checks.disposable_domain:
            score = min(score, 15)
            signals.insert(0, 'Disposable/temporary email domain detected — treat as high risk')

        if checks.free_email_provider:
            score -= 10
            signals.append('Free webmail provider — verify sender identity separately')

        if checks.role_account:
            score -= 5
            signals.append('Role-based mailbox (not a personal address)')

    score = max(0, min(100, score))
    likely_legit = (
        checks.format_valid
        and not checks.disposable_domain
        and score >= 55
        and bool(domain_checks.mx_records or domain_checks.a_records)
    )

    return {
        'input_type': 'email',
        'input_value': checks.email,
        'score': score,
        'is_likely_legit': likely_legit,
        'recommendation': _recommendation(
            score,
            domain_checks.mx_records,
            disposable=checks.disposable_domain,
            free_provider=checks.free_email_provider,
        ),
        'checks': {
            'format_valid': checks.format_valid,
            'local_part': checks.local_part,
            'domain': checks.domain,
            'disposable_domain': checks.disposable_domain,
            'free_email_provider': checks.free_email_provider,
            'role_account': checks.role_account,
            'domain_checks': asdict(domain_checks),
        },
        'signals': signals,
    }


def _recommendation(
    score: int,
    mx_records: List[str],
    disposable: bool = False,
    free_provider: bool = False,
) -> str:
    if disposable:
        return 'High risk — likely a throwaway email address despite any mail DNS records'
    if score >= 80:
        return 'Likely legitimate — domain appears configured for real email'
    if score >= 60:
        return 'Probably legitimate — some mail infrastructure signals present'
    if free_provider:
        return 'Mixed signal — personal webmail; confirm recruiter identity out-of-band'
    if not mx_records:
        return 'Suspicious — domain does not appear set up to receive email'
    return 'Low confidence — treat with caution before replying or clicking links'
