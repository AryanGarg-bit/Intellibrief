"""Email HTML and Plain-Text rendering for daily intelligence briefings."""

import html
from typing import List, Tuple
from app.personalization.select_stories import SelectionResult
from app.config import settings


def generate_executive_summary(selection: SelectionResult) -> str:
    """Generate a concise 3-4 line executive summary of today's key stories."""
    fin_count = len(selection.finance_stories)
    tech_count = len(selection.technology_stories)

    lines = [
        f"Today's briefing covers {fin_count} key Finance and {tech_count} Technology developments.",
    ]

    if selection.finance_stories:
        top_fin = selection.finance_stories[0].title
        lines.append(f"• In Finance: {top_fin}")

    if selection.technology_stories:
        top_tech = selection.technology_stories[0].title
        lines.append(f"• In Tech: {top_tech}")

    return "\n".join(lines)


def render_story_html(story) -> str:
    """Render a single story block in HTML."""
    safe_title = html.escape(story.title)
    safe_source = html.escape(story.source_name)
    safe_summary = html.escape(story.summary or story.content_excerpt or "")
    safe_why = html.escape(story.why_it_matters or "")
    safe_url = html.escape(story.source_url)
    date_str = story.published_at.strftime("%b %d, %Y")

    return f"""
    <div style="margin-bottom: 24px; padding-bottom: 18px; border-bottom: 1px solid #e2e8f0;">
      <div style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
        {story.category} &bull; {story.region} &bull; {date_str}
      </div>
      <h3 style="margin: 0 0 8px 0; font-size: 17px; line-height: 1.4; color: #0f172a;">
        <a href="{safe_url}" style="color: #0284c7; text-decoration: none;" target="_blank">{safe_title}</a>
      </h3>
      <p style="margin: 0 0 8px 0; font-size: 14px; line-height: 1.6; color: #334155;">
        {safe_summary}
      </p>
      {f'<div style="font-size: 13px; color: #475569; background: #f8fafc; padding: 8px 12px; border-left: 3px solid #0ea5e9; margin-top: 8px;"><strong>Why it matters:</strong> {safe_why}</div>' if safe_why else ''}
      <div style="margin-top: 8px; font-size: 12px; color: #94a3b8;">
        Source: <a href="{safe_url}" style="color: #64748b;" target="_blank">{safe_source}</a>
      </div>
    </div>
    """


def render_email(
    report_date: str,
    selection: SelectionResult,
    user_email: str,
    user_id: str,
) -> Tuple[str, str, str]:
    """
    Render both HTML and Plain-Text representations of the daily briefing.
    Returns (subject, html_content, text_content).
    """
    subject = f"Your Daily Intelligence Briefing — {report_date}"
    exec_summary = generate_executive_summary(selection)

    manage_url = f"{settings.app_base_url}/preferences?user_id={user_id}"
    unsubscribe_url = f"{settings.app_base_url}/unsubscribe?email={user_email}"

    # Build HTML
    fin_html = "".join(render_story_html(s) for s in selection.finance_stories)
    if selection.finance_shortage_note:
        fin_html += f'<div style="padding: 10px; background: #fffbeb; color: #b45309; font-size: 13px; border-radius: 4px; margin-bottom: 16px;">Notice: {html.escape(selection.finance_shortage_note)}</div>'

    tech_html = "".join(render_story_html(s) for s in selection.technology_stories)
    if selection.tech_shortage_note:
        tech_html += f'<div style="padding: 10px; background: #fffbeb; color: #b45309; font-size: 13px; border-radius: 4px; margin-bottom: 16px;">Notice: {html.escape(selection.tech_shortage_note)}</div>'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(subject)}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px 12px; color: #0f172a;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
          <!-- Header -->
          <tr>
            <td style="padding: 24px 32px; background: #0f172a; color: #ffffff;">
              <h1 style="margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">IntelliBrief</h1>
              <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">Daily Finance &amp; Technology Briefing &bull; {report_date}</p>
            </td>
          </tr>

          <!-- Executive Summary -->
          <tr>
            <td style="padding: 24px 32px 16px 32px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
              <h2 style="margin: 0 0 10px 0; font-size: 15px; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Executive Summary</h2>
              <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #334155; white-space: pre-line;">{html.escape(exec_summary)}</p>
            </td>
          </tr>

          <!-- Finance Section -->
          <tr>
            <td style="padding: 24px 32px 8px 32px;">
              <h2 style="margin: 0 0 16px 0; font-size: 18px; color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 6px;">
                📈 Finance Developments ({len(selection.finance_stories)}/5)
              </h2>
              {fin_html}
            </td>
          </tr>

          <!-- Technology Section -->
          <tr>
            <td style="padding: 8px 32px 24px 32px;">
              <h2 style="margin: 0 0 16px 0; font-size: 18px; color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 6px;">
                💻 Technology Developments ({len(selection.technology_stories)}/5)
              </h2>
              {tech_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 32px; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; text-align: center;">
              <p style="margin: 0 0 8px 0;">You received this email because you subscribed to daily briefings on IntelliBrief.</p>
              <p style="margin: 0;">
                <a href="{manage_url}" style="color: #0284c7; text-decoration: underline;">Manage Preferences</a> &bull; 
                <a href="{unsubscribe_url}" style="color: #64748b; text-decoration: underline;">Unsubscribe</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # Build Plain-Text alternative
    text_lines = [
        f"INTELLIBRIEF — Daily Briefing ({report_date})",
        "=" * 40,
        "",
        "EXECUTIVE SUMMARY:",
        exec_summary,
        "",
        f"FINANCE STORIES ({len(selection.finance_stories)}/5):",
        "-" * 30,
    ]
    for s in selection.finance_stories:
        text_lines.append(f"• {s.title} ({s.source_name})")
        text_lines.append(f"  {s.summary or s.content_excerpt}")
        text_lines.append(f"  Link: {s.source_url}")
        text_lines.append("")

    if selection.finance_shortage_note:
        text_lines.append(f"[Note: {selection.finance_shortage_note}]\n")

    text_lines.append(f"TECHNOLOGY STORIES ({len(selection.technology_stories)}/5):")
    text_lines.append("-" * 30)
    for s in selection.technology_stories:
        text_lines.append(f"• {s.title} ({s.source_name})")
        text_lines.append(f"  {s.summary or s.content_excerpt}")
        text_lines.append(f"  Link: {s.source_url}")
        text_lines.append("")

    if selection.tech_shortage_note:
        text_lines.append(f"[Note: {selection.tech_shortage_note}]\n")

    text_lines.append("-" * 40)
    text_lines.append(f"Manage preferences: {manage_url}")
    text_lines.append(f"Unsubscribe: {unsubscribe_url}")

    text_content = "\n".join(text_lines)

    return subject, html_content, text_content
