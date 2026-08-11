import os
import sys
import argparse
import html
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Headless 백엔드 설정 (서버/클라우드 디스플레이 미지원 환경)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dotenv import load_dotenv

# Windows 콘솔 출력 UTF-8 설정
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '').strip()

# 차트 스타일 및 한글 폰트 설정 (서버 환경 호환)
plt.style.use('dark_background')
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def fetch_stock_data():
    """S&P 500 (^GSPC) 및 NASDAQ (^IXIC) 최근 1개월 데이터 수집"""
    print("[1/4] S&P 500 및 NASDAQ 지수 데이터 수집 중...")
    sp500 = yf.Ticker('^GSPC')
    nasdaq = yf.Ticker('^IXIC')

    sp500_hist = sp500.history(period='1mo')
    nasdaq_hist = nasdaq.history(period='1mo')

    if sp500_hist.empty or nasdaq_hist.empty:
        raise ValueError("지수 데이터를 가져오는데 실패했습니다.")

    return {
        'sp500': {
            'ticker': '^GSPC',
            'name': 'S&P 500',
            'hist': sp500_hist,
            'ticker_obj': sp500
        },
        'nasdaq': {
            'ticker': '^IXIC',
            'name': 'NASDAQ',
            'hist': nasdaq_hist,
            'ticker_obj': nasdaq
        }
    }


def generate_stock_chart(data, output_path='stock_chart.png'):
    """가독성을 대폭 향상시킨 S&P 500 및 NASDAQ 고화질 대형 차트 생성"""
    print("[2/4] 고화질 대형 차트 이미지 생성 중...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 11), sharex=True)
    fig.patch.set_facecolor('#0D1117')

    for ax in (ax1, ax2):
        ax.set_facecolor('#161B22')
        ax.grid(True, color='#30363D', linestyle='--', linewidth=1.0, alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#8B949E')
        ax.spines['bottom'].set_color('#8B949E')
        ax.tick_params(colors='#C9D1D9', labelsize=14, length=6)

    # 1. S&P 500 서브플롯
    sp_hist = data['sp500']['hist']
    sp_latest = sp_hist['Close'].iloc[-1]
    sp_prev = sp_hist['Close'].iloc[-2]
    sp_change = sp_latest - sp_prev
    sp_pct = (sp_change / sp_prev) * 100
    sp_color = '#2EA043' if sp_change >= 0 else '#F85149'

    sp_ma5 = sp_hist['Close'].rolling(window=5).mean()
    sp_ma20 = sp_hist['Close'].rolling(window=20).mean()

    ax1.plot(sp_hist.index, sp_hist['Close'], color=sp_color, linewidth=3.5, label='Close (S&P 500)')
    if not sp_ma5.dropna().empty:
        ax1.plot(sp_hist.index, sp_ma5, color='#F2C94C', linewidth=2.0, linestyle=':', label='5-Day MA')
    if not sp_ma20.dropna().empty:
        ax1.plot(sp_hist.index, sp_ma20, color='#BB6BD9', linewidth=2.0, linestyle='--', label='20-Day MA')

    ax1.fill_between(sp_hist.index, sp_hist['Close'], sp_hist['Close'].min() * 0.995, color=sp_color, alpha=0.18)
    
    sign_sp = "+" if sp_change >= 0 else ""
    ax1.set_title(f"  S&P 500 Index : {sp_latest:,.2f}  ({sign_sp}{sp_change:,.2f}, {sign_sp}{sp_pct:.2f}%)", 
                  color=sp_color, fontsize=20, fontweight='bold', loc='left', pad=15)
    ax1.legend(loc='upper left', fontsize=12, facecolor='#21262D', edgecolor='#30363D', labelcolor='#C9D1D9')

    # 2. NASDAQ 서브플롯
    nq_hist = data['nasdaq']['hist']
    nq_latest = nq_hist['Close'].iloc[-1]
    nq_prev = nq_hist['Close'].iloc[-2]
    nq_change = nq_latest - nq_prev
    nq_pct = (nq_change / nq_prev) * 100
    nq_color = '#2EA043' if nq_change >= 0 else '#F85149'

    nq_ma5 = nq_hist['Close'].rolling(window=5).mean()
    nq_ma20 = nq_hist['Close'].rolling(window=20).mean()

    ax2.plot(nq_hist.index, nq_hist['Close'], color=nq_color, linewidth=3.5, label='Close (NASDAQ)')
    if not nq_ma5.dropna().empty:
        ax2.plot(nq_hist.index, nq_ma5, color='#F2C94C', linewidth=2.0, linestyle=':', label='5-Day MA')
    if not nq_ma20.dropna().empty:
        ax2.plot(nq_hist.index, nq_ma20, color='#BB6BD9', linewidth=2.0, linestyle='--', label='20-Day MA')

    ax2.fill_between(nq_hist.index, nq_hist['Close'], nq_hist['Close'].min() * 0.995, color=nq_color, alpha=0.18)
    
    sign_nq = "+" if nq_change >= 0 else ""
    ax2.set_title(f"  NASDAQ Composite : {nq_latest:,.2f}  ({sign_nq}{nq_change:,.2f}, {sign_nq}{nq_pct:.2f}%)", 
                  color=nq_color, fontsize=20, fontweight='bold', loc='left', pad=15)
    ax2.legend(loc='upper left', fontsize=12, facecolor='#21262D', edgecolor='#30363D', labelcolor='#C9D1D9')

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    fig.autofmt_xdate(rotation=25)

    plt.suptitle(f"US Stock Market Chart Analysis - {datetime.now().strftime('%Y-%m-%d')}", 
                 color='#FFFFFF', fontsize=22, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"  └> 고화질 차트 저장 완료: {output_path}")

    return {
        'sp500': {'latest': sp_latest, 'change': sp_change, 'pct': sp_pct, 'hist': sp_hist},
        'nasdaq': {'latest': nq_latest, 'change': nq_change, 'pct': nq_pct, 'hist': nq_hist}
    }


def fetch_korean_domestic_news(limit=10):
    """국내 주요 언론사의 미국 증시/S&P500/나스닥 한글 뉴스 10개 수집"""
    print(f"[3/4] 국내 언론사의 미국 증시 실시간 뉴스 {limit}개 수집 중...")
    news_list = []
    
    rss_urls = [
        "https://news.google.com/rss/search?q=S%26P500+%EB%82%98%EC%8A%A4%EB%8B%A5+%EB%AF%B8%EA%B5%AD%EC%A6%89%EC%8B%9C&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/search?q=%EB%AF%B8%EA%B5%AD+%EC%A6%89%EC%8B%9C+%EB%85%90%EC%96%9D%EC%A6%89%EC%8B%9C+%EA%B8%B0%EC%88%A0%EC%A3%BC&hl=ko&gl=KR&ceid=KR:ko"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for rss_url in rss_urls:
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    source_elem = item.find('source')

                    raw_title = title_elem.text if title_elem is not None else ""
                    link = link_elem.text if link_elem is not None else ""
                    publisher = source_elem.text if source_elem is not None else "국내 언론사"

                    clean_title = raw_title
                    if " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        clean_title = parts[0]
                        if publisher == "국내 언론사":
                            publisher = parts[1]

                    if clean_title and link and not any(n['title'] == clean_title for n in news_list):
                        news_list.append({
                            'title': clean_title,
                            'link': link,
                            'publisher': publisher
                        })
                    
                    if len(news_list) >= limit:
                        break
        except Exception as e:
            print(f"⚠️ 뉴스 수집 중 오류: {e}")
            
        if len(news_list) >= limit:
            break

    return news_list


def generate_ai_investment_analysis(summary_stats, news_list):
    """S&P 500 및 나스닥 지수 기술적 분석 + 국내 주요 기사 결합 AI 투자 분석 (HTML 출력)"""
    sp_hist = summary_stats['sp500']['hist']['Close']
    nq_hist = summary_stats['nasdaq']['hist']['Close']

    sp_latest = sp_hist.iloc[-1]
    sp_ma5 = sp_hist.tail(5).mean()
    sp_ma20 = sp_hist.tail(20).mean()

    nq_latest = nq_hist.iloc[-1]
    nq_ma5 = nq_hist.tail(5).mean()
    nq_ma20 = nq_hist.tail(20).mean()

    analysis = []

    # 1. 단기 시장 추세 평가
    if sp_latest >= sp_ma5 and nq_latest >= nq_ma5:
        trend_summary = "🟢 <b>상승 모멘텀 지속</b>: S&P 500과 나스닥 모두 5일 이동평균선 위에서 거래되며 매수세가 견조합니다."
    elif sp_latest < sp_ma5 and nq_latest < sp_ma5:
        trend_summary = "🔴 <b>단기 숨고르기/조정</b>: 주요 지수가 5일 이동평균선을 하회하며 단기 차익 실현 물량이 출회 중입니다."
    else:
        trend_summary = "🟡 <b>차별화 장세</b>: 대형주(S&P 500)와 기술주(NASDAQ) 간 향방이 갈리며 뚜렷한 눈치보기 장세입니다."
    
    analysis.append(trend_summary)

    # 2. 지수별 기술적 위치 분석
    sp_status = "20일선 상회(중기 정배열)" if sp_latest >= sp_ma20 else "20일선 하회(주의 필요)"
    nq_status = "20일선 상회(중기 정배열)" if nq_latest >= nq_ma20 else "20일선 하회(주의 필요)"
    
    analysis.append(f"· <b>S&P 500</b>: <code>{sp_latest:,.2f}pt</code> ({sp_status}) -&gt; 대형 우량주 중심 자금 방어력 양호")
    analysis.append(f"· <b>나스닥(NASDAQ)</b>: <code>{nq_latest:,.2f}pt</code> ({nq_status}) -&gt; 기술주/AI 섹터 투자 심리 민감 반응")

    # 3. 맞춤형 일일 투자 전략 가이드
    analysis.append("\n💡 <b>오늘의 AI 투자 포인팅 &amp; 전략</b>:")
    if sp_latest >= sp_ma20 and nq_latest >= nq_ma20:
        analysis.append("  1. <b>추세 추종 유효</b>: 전체적인 시장 추세가 양호하므로 대형 기술주 및 핵심 지수 ETF 분할 매수 접근 유효.")
        analysis.append("  2. <b>주요 발표 리스크 대비</b>: 거시경제 지표(CPI, 미 연준 스탠스) 일정 확인 후 신규 진입 비중 조절 추천.")
    else:
        analysis.append("  1. <b>현금 비중 관리</b>: 단기 변동성 확대 구간이므로 섣부른 뇌동매수보다는 지지선 확인 후 접근 권장.")
        analysis.append("  2. <b>방어주/고배당 섹터 관심</b>: 기술주 변동성에 대비해 실적 안정성이 뛰어난 방어주 및 대표 ETF 비중 유지 유효.")

    return "\n".join(analysis)


def compose_briefing_message(summary_stats, news_list):
    """텔레그램 메시지 텍스트 조합 (HTML 포맷, 10개 뉴스 포함)"""
    today_str = datetime.now().strftime('%Y년 %m월 %d일')
    
    sp = summary_stats['sp500']
    nq = summary_stats['nasdaq']

    sp_icon = "🟢" if sp['change'] >= 0 else "🔴"
    nq_icon = "🟢" if nq['change'] >= 0 else "🔴"

    sign_sp = "+" if sp['change'] >= 0 else ""
    sign_nq = "+" if nq['change'] >= 0 else ""

    msg = f"📊 <b>[미국 증시 데일리 브리핑 - {today_str}]</b>\n\n"
    
    # 지수 수치
    msg += f"🔹 <b>S&P 500</b>\n"
    msg += f"  · 종가: <code>{sp['latest']:,.2f}</code>\n"
    msg += f"  · 변동: {sp_icon} <code>{sign_sp}{sp['change']:,.2f}</code> (<code>{sign_sp}{sp['pct']:.2f}%</code>)\n\n"

    msg += f"🔹 <b>NASDAQ 종합지수</b>\n"
    msg += f"  · 종가: <code>{nq['latest']:,.2f}</code>\n"
    msg += f"  · 변동: {nq_icon} <code>{sign_nq}{nq['change']:,.2f}</code> (<code>{sign_nq}{nq['pct']:.2f}%</code>)\n\n"

    # AI 투자 분석 섹션
    ai_analysis = generate_ai_investment_analysis(summary_stats, news_list)
    msg += f"🧠 <b>AI 일일 증시 투자 분석 &amp; 전략</b>\n{ai_analysis}\n\n"

    # 국내 언론사 한글 기사 10개 리스트
    msg += f"📰 <b>국내 주요 언론사 미국 증시 핵심 뉴스 (Top {len(news_list)})</b>\n"
    if news_list:
        for idx, news in enumerate(news_list, 1):
            safe_title = html.escape(news['title'])
            safe_link = html.escape(news['link'], quote=True)
            safe_publisher = html.escape(news['publisher'])
            msg += f"{idx}. <a href=\"{safe_link}\">{safe_title}</a> <i>({safe_publisher})</i>\n"
    else:
        msg += "· 현재 수집된 최신 국내 뉴스가 없습니다.\n"

    msg += "\n🤖 <i>AI Daily Stock Briefing Engine</i>"
    return msg


def send_to_telegram(image_path, text_message):
    """텔레그램 API를 사용하여 차트 이미지와 10개 뉴스 브리핑 메세지 발송 (HTML 모드)"""
    print("[4/4] 텔레그램 전송 시도 중...")
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE' or \
       not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == 'YOUR_TELEGRAM_CHAT_ID_HERE':
        print("⚠️ 환경변수에 TELEGRAM_BOT_TOKEN 및 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return False

    url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        # 1. 고화질 차트 이미지 먼저 깔끔하게 전송
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            payload = {'chat_id': TELEGRAM_CHAT_ID}
            requests.post(url_photo, data=payload, files=files, timeout=30)
            print("  └> 차트 이미지 전송 완료")

        # 2. 10개 전체 뉴스와 AI 분석 텍스트 메세지 전송 (HTML 파싱 사용)
        msg_payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text_message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        res_msg = requests.post(url_msg, data=msg_payload, timeout=30)

        if res_msg.status_code == 200:
            print("✅ 텔레그램으로 고화질 차트 및 국내 뉴스 10개 브리핑 전송 성공!")
            return True
        else:
            print(f"❌ 메시지 전송 실패 (상태 코드: {res_msg.status_code}) - {res_msg.text}")
            return False

    except Exception as e:
        print(f"❌ 텔레그램 전송 중 오류 발생: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="미국 증시 텔레그램 자동 브리핑")
    parser.add_argument('--dry-run', action='store_true', help="텔레그램 전송 없이 로컬 생성만 진행")
    args = parser.parse_args()

    chart_file = os.path.join(os.path.dirname(__file__), 'stock_chart.png')

    try:
        data = fetch_stock_data()
        summary_stats = generate_stock_chart(data, output_path=chart_file)
        news_list = fetch_korean_domestic_news(limit=10)
        message = compose_briefing_message(summary_stats, news_list)

        print("\n--- 📋 국내 뉴스 10개 브리핑 메세지 미리보기 (HTML) ---")
        print(message)
        print("------------------------------------------------\n")

        if args.dry_run:
            print("ℹ️ --dry-run 옵션으로 실행되어 텔레그램 전송을 건너뜁니다.")
        else:
            send_to_telegram(chart_file, message)

    except Exception as e:
        print(f"💥 스크립트 실행 중 에러가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
