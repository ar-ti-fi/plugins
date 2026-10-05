"""Render incomplete source components without inventing totals or ratios."""
from decimal import Decimal, InvalidOperation

MONEY_FIELDS = {'amount', 'balance', 'debit', 'credit', 'total', 'current', 'days_1_30',
    'days_31_60', 'days_61_90', 'days_over_90', 'days_90_plus', 'net_income', 'net_profit',
    'opening_balance', 'closing_balance', 'original_cost', 'net_book_value'}

def incomplete_report(data):
    quality = data.get('quality') or data.get('report_v1', {}).get('quality', {})
    rows = []
    missing = False
    def visit(value, path=''):
        nonlocal missing
        if isinstance(value, list):
            for item in value:
                visit(item, path)
        elif isinstance(value, dict):
            label = value.get('name') or value.get('account_name') or value.get('party_name') or path
            for key, item in value.items():
                if key in ('report_v1', 'quality', 'evidence_gaps'):
                    continue
                if key in MONEY_FIELDS or key.startswith('total_') or key.endswith('_amount') or key.endswith('_balance'):
                    if isinstance(item, (dict, list)):
                        visit(item, f'{path} {key}'.strip())
                    elif item is None:
                        missing = True
                        rows.append((f'{label} · {key.replace("_", " ")}', 'Unavailable'))
                    else:
                        try:
                            amount = Decimal(str(item))
                            if amount.is_finite(): rows.append((f'{label} · {key.replace("_", " ")}', str(amount)))
                        except InvalidOperation:
                            pass
                elif isinstance(item, (dict, list)):
                    visit(item, f'{path} {key.replace("_", " ")}'.strip())
    visit(data)
    if not missing and quality.get('status') != 'incomplete':
        return None
    def escape(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    result = ['# Financial report — incomplete', '',
        f'**{escape(data.get("entity_name", "Selected entity"))}** | Currency: {escape(data["currency"])}', '',
        'Some amounts are unavailable. Known source components are shown below; no totals or ratios have been inferred.', '']
    result.extend(escape(g['message']) for g in quality.get('evidence_gaps', []) if g.get('message'))
    result.extend(['', '| Component | Amount |', '|---|---:|'])
    result.extend(f'| {escape(label)} | {escape(amount)} |' for label, amount in rows[:200])
    if len(rows)>200: result.extend(['', f'Showing 200 of {len(rows)} source components. Request the full report for remaining rows.'])
    return '\n'.join(result)
