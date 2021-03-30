STATISTIC = "http://ipam.mchs.ru/report/statistic"

'''
Set html patterns
'''
html_patterns = [
    r'<a\s.+?>\s?([^(\n|?:{{|<)].+?[^(?:}}|>|\n)])<\/a>',
    r'<th>\s?([^(\n|?:{{|<)].+?[^(?:}}|>)])</th>',
    r'<th\s.+?>\s?([^(\n|?:{{|<)].+?[^(?:}}|>)])</th>',
    r'<td>\s?([^(\n|?:{{|<|\")].+?[^(?:}}|>|\")])</td>',
    r'<td\s.+?>\s?([^(\n|?:{{|<|\")].+?[^(?:}}|>|\")])</td>',
    r'\splaceholder=\"(.+?)\"',
    r'\stitle=\"([^(?:\.ui\-icon\-|?:{{)].+?)\"',
    r'<p(?:\s.+)?>(?!{[{\%])(?!<a)(.+?[^>])(?!</a>)(?!}[\%}])<\/p>',
    r'<h\d(?:\s.+)?>(?!{[{\%])(?!<a)(.+?[^(?:</a>])(?!}[\%}])<\/h\d>',
    r'<button\s?.*?>(?!{{)(.+?[^>])(?!}})</button>',
    r'</span>\s+(.+?[^>])\n\s*?</button>',
    r'</span>\s+(.+?[^>])\n\s*?</a>',
    r'</i>\s+(.+?[^>])\n\s*?</div>',
    r'</i>\s*?(.+?[^>])\s*?</a>',
    r'<title\s?.*?>(?!{{)(.+?)(?!}})</title>',
    r'<label\s?.*?>(?!{{)(.+?)(?!}})</label>',
    r'<strong\s?.*?>(?!{{)(.+?[^>])(?!}})</strong>',
    r'<li(?:.+)?>(?!<a)(?!<span)(?!{{)(.+?[^>])(?!}})</li>',
    r'<input type=\"submit\".+value=\"\s?(\w+)\s?\"\s?/>',
    r'>\s?(\w+)\s?<span',
    r'<\/span>\s?([\w\s]+)\s?<span',
    r'<div class="panel-body text-muted">\s?([\w\s]+)<\/div>',
    r'(?!=</i>)([\sA-Z][A-Za-z]+)</button>',
    r'(?!=\">)([A-Za-z]{3,})(?=[\s]?{{)',
    r'(?!=%})[\s\b]?([A-Za-z+\s?]{3,})\b(?=[\s]?{{)',
    r'(?!=</select>)(\b[\w ]+)\n'
]

phrases_patterns = [
    r'verbose_name\s?=\s?[\'\"](.+)[\'\"]',
    r'help_text\s?=\s?([\'\"](.+)[\'\"])',
    r'verbose_name_plural\s?=\s?[\'\"](.+)[\'\"]',
    r'label\s?=\s?[\'\"](.+)[\'\"]'
]


html_dict = {
    "statistic": {
        "search": "<a href=\"{% url 'extras:report_list' %}\">Reports</a>",
        "search_r": "<a href=\"{% url 'extras:report_list' %}\">Отчеты</a>",
        "swap": "\t\t\t\t\t\t<li class=\"divider\"></li>\n"
                "\t\t\t\t\t\t<li{% if not perms.extras.view_report %} class=\"disabled\"{%endif %}>\n"
                f"\t\t\t\t\t\t\t<a href=\"{STATISTIC}\">Статистика</a>\n"
                "\t\t\t\t\t\t</li>\n"

    }
}