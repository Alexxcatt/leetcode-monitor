import json
import os
from datetime import datetime, timezone, timedelta
import requests

import config as project_config

LEETCODE_GRAPHQL_URL = 'https://leetcode.cn/graphql/noj-go/'

HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://leetcode.cn',
    'Referer': 'https://leetcode.cn/u/{}/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'authorization': ';',
    'content-type': 'application/json',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

CHINA_TIMEZONE = timezone(timedelta(hours=8))


# 获取用户的提交日历
def get_user_submission_calendar(name: str):
    data = {
        "query": "query userProfileCalendar($userSlug: String!, $year: Int) {\n userCalendar(userSlug: $userSlug, year: $year) {\n streak\n totalActiveDays\n submissionCalendar\n activeYears\n monthlyMedals {\n name\n obtainDate\n category\n config {\n icon\n iconGif\n iconGifBackground\n }\n progress\n id\n year\n month\n }\n recentStreak\n }\n}",
        "variables": {"userSlug": name},
        "operationName": "userProfileCalendar"
    }
    headers = HEADERS.copy()
    headers['Referer'] = headers['Referer'].format(name)
    headers['x-definition-name'] = 'userProfileCalendar'
    headers['x-operation-name'] = 'userProfileCalendar'
    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            headers=headers,
            json=data,
            timeout=20,
        )
        response.raise_for_status()
        response_json = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f'获取用户 {name} 的力扣数据失败: {exc}') from exc

    user_calendar = response_json.get('data', {}).get('userCalendar')
    if not user_calendar:
        raise ValueError(f'力扣用户不存在或日历不可用: {name}')
    submission_calendar = json.loads(user_calendar['submissionCalendar'])
    return submission_calendar


# 获取最后一次的提交日期、提交次数
def get_last_submission(submission_calendar):
    if not submission_calendar:
        return None, 0
    timestamps = list(submission_calendar.keys())
    last_day_timestamp = max(map(int, timestamps))
    last_day_datetime = datetime.fromtimestamp(last_day_timestamp, CHINA_TIMEZONE)
    last_day_date = last_day_datetime.strftime('%Y-%m-%d')
    last_day_submissions = submission_calendar[str(last_day_timestamp)]
    return last_day_date, last_day_submissions


def get_daily_submissions(submission_calendar, day=None):
    """返回中国时区指定日期的提交数，无提交时返回 0。"""
    target_day = day or datetime.now(CHINA_TIMEZONE).date()
    for timestamp, count in submission_calendar.items():
        submission_day = datetime.fromtimestamp(int(timestamp), CHINA_TIMEZONE).date()
        if submission_day == target_day:
            return count
    return 0


def do_monitor():
    config = project_config.load_config()
    users = config['users']
    results = []
    today = datetime.now(CHINA_TIMEZONE).date()
    for user in users:
        submission_calendar = get_user_submission_calendar(user)
        last_day_date, last_day_submissions = get_last_submission(submission_calendar)
        today_submissions = get_daily_submissions(submission_calendar, today)
        results.append((user, today_submissions, last_day_date, last_day_submissions))

    output_lines = [f"力扣每日打卡（中国时间 {today.isoformat()}）"]
    for name, today_submissions, last_day_date, last_day_submissions in results:
        output_lines.append(f"{name}: 今日提交 {today_submissions} 次")
        if today_submissions == 0 and last_day_date:
            output_lines.append(
                f"  最近提交: {last_day_date}，{last_day_submissions} 次"
            )
    output_string = "\n".join(output_lines)
    print(output_string)

    github_summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if github_summary:
        with open(github_summary, 'a', encoding='utf-8') as summary_file:
            summary_file.write(f"## {output_lines[0]}\n\n")
            summary_file.write("\n\n".join(output_lines[1:]) + "\n")

    # 根据配置的不同发送消息
    channel_type = config.get('channel_type', 'console')
    if channel_type == 'telegram':
        import asyncio
        from channel_bot import telegram_bot
        asyncio.run(telegram_bot.send(output_string))
    elif channel_type == 'dingding':
        from channel_bot import dingding_bot
        dingding_bot.send(output_string)
    elif channel_type != 'console':
        raise ValueError(f'不支持的 channel_type: {channel_type}')

    return results


def main():
    do_monitor()


if __name__ == '__main__':
    main()
