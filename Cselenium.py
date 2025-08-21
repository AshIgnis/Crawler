from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import random
import threading
import msvcrt  # Windows下的按键检测
import sys

# 代理服务器列表 (HOST:PORT格式)
proxy_arr = [
    '182.106.136.217:21072',
    '61.184.8.27:20909',
    '36.25.243.10:20501',
    '221.229.212.173:25114',
    '61.184.8.27:20424',
    '49.73.231.237:21698',
    '182.106.136.217:21467',
    '182.106.136.217:20222',
    '221.234.30.227:20279',
    '119.102.159.103:15726',
    '114.104.238.246:19534',
    '218.95.37.135:21599',
    '61.184.8.27:21330',
    '182.106.136.217:20464',
    '58.19.54.132:21108',
    '61.184.8.27:20562',
    '117.28.191.169:22990',
    '119.102.158.79:17945',
    '116.208.200.185:18434',
    '218.95.37.135:20150',
    '49.87.220.133:20580',
    '117.86.203.7:17866',
    '116.208.204.206:17803',
    '182.106.136.217:20269',
    '182.106.136.217:20815',
    '61.184.8.27:20366',
    '218.95.37.251:25059',
    '218.95.37.11:25086',
    '58.19.54.132:20665',
    '218.95.37.251:25026'
]

# 当前使用的代理索引
current_proxy_index = 0
used_proxies = []
quit_flag = False  # 退出标志
driver = None
chrome_options = None

def save_and_exit(result_list):
    """保存当前数据并退出程序"""
    print(f"\n📊 正在保存数据...")
    print(f"共采集了 {len(result_list)} 条房源数据")
    
    if result_list:
        try:
            df = pd.DataFrame(result_list)
            df.to_excel('lianjia_data_partial.xlsx', index=False)
            print(f"✅ 数据已保存到: lianjia_data_partial.xlsx")
            print(f"📋 数据摘要:")
            print(f"   - 总条数: {len(result_list)}")
            print(f"   - 包含字段: {list(result_list[0].keys()) if result_list else '无'}")
        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")
    else:
        print("⚠️ 没有数据可保存")
    
    print("👋 程序已退出")
    try:
        if driver:
            driver.quit()
    except:
        pass
    sys.exit(0)

def extract_house_data_fast(driver):
    """超快速提取房源数据的优化函数，增强容错能力"""
    data_dict = {
        "区域": "",  # 添加区域字段
        "标题": "",
        "地区": "",
        "户型": "",
        "面积": "",
        "朝向": "",
        "装修": "",
        "楼层": "",
        "建立时间": "",
        "房子类型": "",
        "总价": "",
        "单价": "",
        "关注人数": "",
    }
    
    try:
        # 多套选择器方案，提高数据获取成功率
        selectors = {
            '标题': ['h1.main', 'h1', '.title h1', '.house-title'],
            '地区': ['a.info', '.area-info a', '.location a', '.community a'], 
            '户型': ['div.room > div.mainInfo', '.room-info', '.house-type', '.layout'],
            '面积': ['div.area > div.mainInfo', '.area-info', '.house-area', '.size'],
            '朝向': ['div.type > div.mainInfo', '.orientation', '.direction', '.facing'],
            '总价': ['div.price span.total', '.total-price', '.price .total', '.house-price .total'],
            '单价': ['div.unitPrice span.unitPriceValue', '.unit-price', '.price-per-sqm', '.unitPrice'],
        }
        
        # 使用多套选择器提高成功率
        for key, selector_list in selectors.items():
            for selector in selector_list:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text:  # 只有非空文本才使用
                        data_dict[key] = text
                        break  # 成功获取到数据就停止尝试其他选择器
                except:
                    continue  # 当前选择器失败，尝试下一个
        
        # 获取关注人数（多种选择器）
        fav_selectors = ['span#favCount', '.favor-count', '.watch-count', '.attention-count']
        for selector in fav_selectors:
            try:
                fav_count = driver.find_element(By.CSS_SELECTOR, selector)
                text = fav_count.text.strip()
                if text:
                    data_dict['关注人数'] = text
                    break
            except:
                continue
            
        # 获取装修和楼层信息
        detail_selectors = [
            'div.room > div.subInfo',
            'div.type > div.subInfo', 
            '.decoration-info',
            '.floor-info'
        ]
        
        for selector in detail_selectors:
            try:
                detail_element = driver.find_element(By.CSS_SELECTOR, selector)
                detail_text = detail_element.text.strip()
                if '装修' in detail_text or '精装' in detail_text or '简装' in detail_text or '毛坯' in detail_text:
                    data_dict['装修'] = detail_text
                elif '楼层' in detail_text or '层' in detail_text:
                    data_dict['楼层'] = detail_text
            except:
                continue
            
        # 获取房子类型和建立时间（多种方案）
        info_selectors = [
            'div.area > div.subInfo.noHidden',
            '.house-info .sub-info',
            '.building-info',
            '.house-details'
        ]
        
        for selector in info_selectors:
            try:
                house_info = driver.find_element(By.CSS_SELECTOR, selector)
                info_text = house_info.text.strip()
                
                # 解析建立时间和房子类型
                year_match = re.search(r'(\d{4})年建', info_text)
                if year_match:
                    data_dict['建立时间'] = year_match.group(1)
                
                type_match = re.search(r'年建/(.+)', info_text)
                if type_match:
                    data_dict['房子类型'] = type_match.group(1)
                elif info_text and not year_match:
                    data_dict['房子类型'] = info_text
                    
                if data_dict['建立时间'] or data_dict['房子类型']:
                    break  # 成功获取到信息就停止
            except:
                continue
            
    except Exception as e:
        # 静默处理异常，保持高速度
        pass
    
    return data_dict

def key_listener():
    """监听按键输入的线程函数"""
    global quit_flag
    while not quit_flag:
        if msvcrt.kbhit():  # 检查是否有按键
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'q':
                print("\n🚪 检测到退出键 'q'，正在准备退出...")
                quit_flag = True
                return

def create_driver(proxy):
    """创建新的WebDriver实例"""
    global chrome_options, driver
    
    # 重新配置Chrome选项
    chrome_options = webdriver.ChromeOptions()
    
    # 更激进的性能优化选项
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')  # 禁用图片
    chrome_options.add_argument('--disable-java')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-webgl')
    chrome_options.add_argument('--disable-webgl2')
    chrome_options.add_argument('--disable-3d-apis')
    chrome_options.add_argument('--disable-accelerated-2d-canvas')
    chrome_options.add_argument('--disable-css-selectors-api')
    chrome_options.add_argument('--disable-web-security')  # 加速
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')  # 加速
    chrome_options.add_argument('--disable-ipc-flooding-protection')  # 加速
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-background-networking')  # 加速
    chrome_options.add_argument('--disable-default-apps')  # 加速
    chrome_options.add_argument('--disable-sync')  # 加速
    chrome_options.add_argument('--disable-translate')  # 加速
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('--no-first-run')  # 加速
    chrome_options.add_argument('--no-default-browser-check')  # 加速
    chrome_options.add_argument('--disable-component-update')  # 加速
    chrome_options.add_argument('--page-load-strategy=eager')  # 不等所有资源加载完
    
    # 不使用不可靠的 --timeout 参数，统一通过WebDriver API控制超时
    
    # 设置代理
    chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    
    # 关闭旧的 driver（如果有），并短暂等待确保进程退出
    try:
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
            time.sleep(1)
    except Exception:
        pass

    # 创建新的WebDriver实例，带重试以应对临时问题
    max_create_attempts = 3
    last_exc = None
    for attempt in range(1, max_create_attempts + 1):
        try:
            # 减少无关日志
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            driver = webdriver.Chrome(service=Service(), options=chrome_options)
            # 更宽松的超时配置，避免频繁超时
            driver.set_page_load_timeout(30)  # 页面加载30秒超时
            driver.implicitly_wait(3)  # 隐式等待3秒
            return driver
        except Exception as e:
            last_exc = e
            print(f"⚠️ 创建浏览器实例失败 (尝试 {attempt}/{max_create_attempts}): {e}")
            try:
                if driver:
                    driver.quit()
            except:
                pass
            driver = None
            time.sleep(2)

    # 如果多次尝试都失败，抛出最后一个异常
    raise last_exc

def switch_proxy_simple(current_page=1, area_url=None):
    """简化的代理切换函数，增强网络检测"""
    global current_proxy_index, used_proxies, driver
    
    print("🔄 切换代理...")
    
    # 选择下一个代理
    available_proxies = [i for i in range(len(proxy_arr)) if i not in used_proxies]
    if not available_proxies:
        used_proxies.clear()
        available_proxies = list(range(len(proxy_arr)))
    
    current_proxy_index = random.choice(available_proxies)
    new_proxy = proxy_arr[current_proxy_index]
    used_proxies.append(current_proxy_index)
    
    print(f"🔄 使用新代理: {new_proxy}")
    
    # 创建新的浏览器实例（create_driver 会返回新的 driver）
    try:
        driver = create_driver(new_proxy)
    except Exception as e:
        print(f"❌ 创建新浏览器失败: {e}")
        return False
    
    # 访问目标页面
    if area_url:
        if current_page > 1:
            target_url = area_url.rstrip('/') + f"/pg{current_page}/"
        else:
            target_url = area_url
    else:
        target_url = "https://cd.lianjia.com/ershoufang/"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试访问 ({attempt + 1}/{max_retries}): {target_url}")
            driver.get(target_url)
            time.sleep(5)  # 切换代理时等待5秒，让页面和任何认证弹窗出现
            
            # 检查页面是否成功加载
            current_url = driver.current_url
            page_source = driver.page_source
            
            # 检测网络连接问题关键词
            connection_error_keywords = [
                "未连接到互联网",
                "代理服务器出现问题", 
                "ERR_PROXY_CONNECTION_FAILED",
                "ERR_INTERNET_DISCONNECTED",
                "ERR_NETWORK_CHANGED",
                "地址有误",
                "无法访问此网站",
                "网络连接错误"
            ]
            
            # 检查是否有网络连接问题
            if any(keyword in page_source for keyword in connection_error_keywords):
                print(f"❌ 代理 {new_proxy} 连接失败，尝试下一个...")
                continue
                
            # 检查是否成功访问链家网站
            if "lianjia.com" in current_url and len(driver.title) > 0:
                print("✅ 代理切换成功")
                return True
            else:
                print(f"⚠️ 页面状态异常: {current_url[:100]}")
                if attempt < max_retries - 1:
                    continue
                    
        except Exception as e:
            msg = str(e).lower()
            print(f"❌ 访问失败 (尝试{attempt + 1}): {e}")
            # 如果是 invalid session，说明 driver 已经不可用，尝试重新创建一次
            if 'invalid session id' in msg or 'sessiondeleted' in msg or 'session deleted' in msg:
                try:
                    print("⚠️ 检测到无效会话，重新创建浏览器实例并重试...")
                    driver = create_driver(new_proxy)
                except Exception as ce:
                    print(f"❌ 重新创建浏览器失败: {ce}")
                    pass
            if attempt < max_retries - 1:
                time.sleep(2)  # 失败后等待2秒再重试
                continue
            
    print("❌ 代理切换失败")
    return False

# 初始化浏览器
current_proxy_index = random.randint(0, len(proxy_arr) - 1)
proxy = proxy_arr[current_proxy_index]
print(f"使用代理: {proxy} (索引: {current_proxy_index})")

create_driver(proxy)

# 访问链家网站
print("浏览器已启动，正在访问链家网站...")
url = "https://cd.lianjia.com/ershoufang/"

try:
    driver.get(url)
    time.sleep(1)  # 减少初始加载等待时间
    
    current_url = driver.current_url
    print(f"当前URL: {current_url}")
    
    if "lianjia.com" not in current_url:
        print("⚠️ 页面未正常加载，可能需要代理认证")
        input("请完成代理认证并确认页面正常显示后，按回车键继续...")

except Exception as e:
    print(f"访问异常: {e}")
    print("尝试切换代理...")
    if not switch_proxy_simple():
        print("程序将退出")
        sys.exit()

# 获取区域列表（简化版）
def get_area_list():
    """获取成都各区域的链接列表"""
    area_list = [
        {'name': '锦江', 'url': 'https://cd.lianjia.com/ershoufang/jinjiang/'},
        {'name': '青羊', 'url': 'https://cd.lianjia.com/ershoufang/qingyang/'},
        {'name': '武侯', 'url': 'https://cd.lianjia.com/ershoufang/wuhou/'},
        {'name': '高新', 'url': 'https://cd.lianjia.com/ershoufang/gaoxin7/'},
        {'name': '成华', 'url': 'https://cd.lianjia.com/ershoufang/chenghua/'}
    ]
    return area_list

area_list = get_area_list()
print(f"📍 将爬取以下区域: {[area['name'] for area in area_list]}")

result_list = []
url_keywords = ["captcha", "verify", "validate"]

# 启动按键监听线程
print("🎹 按键监听已启动，随时按 'q' 键保存数据并退出程序")
key_thread = threading.Thread(target=key_listener, daemon=True)
key_thread.start()

# 按区域进行爬取
for area_index, area_info in enumerate(area_list, 1):
    if quit_flag:
        break
        
    area_name = area_info['name']
    area_url = area_info['url']
    
    print(f"\n🏙️ 开始爬取区域 [{area_index}/5]: {area_name}")
    
    try:
        # 访问区域页面
        driver.get(area_url)
        time.sleep(1)  # 减少区域页面加载等待时间
        print(f"✅ 成功访问{area_name}区域页面")
        
        area_result_count = 0
        
        # 爬取32页
        consecutive_empty_pages = 0  # 连续未找到房源计数器
        for i in range(1, 33):
            if quit_flag:
                break
                
            print(f"📖 区域 [{area_name}] - 第{i}页/32页 (按 'q' 键随时退出)")
            try:
                # 等待列表区域出现（不抛异常则继续）
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.sellListContent'))
                    )
                except Exception:
                    pass

                # 尝试多次获取房源链接，避免因资源未完全加载而误判
                house_links = []
                attempt_links = 0
                while attempt_links < 3:
                    house_links = driver.find_elements(By.CSS_SELECTOR, 'ul.sellListContent li .title a')
                    if not house_links:
                        # 备用选择器尝试一次
                        alternative_selectors = [
                            'ul.sellListContent li a',
                            '.sell-list-content .title a',
                            '.house-list .title a',
                            'li.clear .title a'
                        ]
                        for selector in alternative_selectors:
                            house_links = driver.find_elements(By.CSS_SELECTOR, selector)
                            if house_links:
                                print(f"使用备用选择器找到房源: {selector}")
                                break
                    if house_links:
                        break
                    # 检查页面是否出现验证码或网络错误关键词，若出现则立即切换代理
                    page_source = driver.page_source.lower()
                    captcha_keywords = ['captcha', 'verify', 'validate', '验证码', '人机验证']
                    network_issues = ['未连接到互联网', '代理服务器出现问题', 'err_proxy_connection_failed', 'err_internet_disconnected']
                    if any(k in page_source for k in captcha_keywords + network_issues):
                        print("🌐 检测到验证码或网络问题，准备切换代理...")
                        if switch_proxy_simple(i, area_url):
                            # 切换代理后，页面已经重新加载到目标页面，重置计数并继续本页重试
                            consecutive_empty_pages = 0
                            attempt_links = 0
                            continue
                        else:
                            break
                    attempt_links += 1
                    time.sleep(1)

                print(f"找到{len(house_links)}个房源链接")

                # 处理连续空结果：如果连续两次抓取不到房源，则认为当前代理不可用并切换一次
                if not house_links:
                    consecutive_empty_pages += 1
                else:
                    consecutive_empty_pages = 0

                if consecutive_empty_pages >= 2:
                    print("⚠️ 连续多次未获取到房源链接，尝试切换代理...")
                    if switch_proxy_simple(i, area_url):
                        consecutive_empty_pages = 0
                        continue
                    else:
                        # 切换失败，继续跳过该页
                        print("⚠️ 切换代理失败，跳过当前页")
                        continue
                        
                # 批量获取所有href，避免在循环中重复DOM查询
                house_hrefs = []
                for link in house_links:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            house_hrefs.append(href)
                    except:
                        continue
                
                for href in house_hrefs:
                    if quit_flag:
                        break
                        
                    try:
                        main_window = driver.current_window_handle
                        driver.execute_script(f"window.open('{href}');")
                        
                        # 快速切换到新窗口
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.2)  # 大幅减少等待时间
                        
                        # 快速检查验证页面
                        current_url = driver.current_url
                        if any(k in current_url.lower() for k in url_keywords):
                            print("🤖 检测到验证页面，切换代理...")
                            driver.close()
                            driver.switch_to.window(main_window)
                            if switch_proxy_simple(i, area_url):
                                break  # 重新获取房源链接
                            continue
                        
                        # 提取数据
                        data_dict = extract_house_data_fast(driver)
                        data_dict['区域'] = area_name
                        result_list.append(data_dict)
                        area_result_count += 1
                        
                        # 减少进度显示频率，每10个显示一次
                        if area_result_count % 10 == 0:
                            print(f"[{area_name}] 已采集 #{area_result_count}: {data_dict.get('标题', '')[:15]}...")
                        
                        # 快速关闭窗口
                        driver.close()
                        driver.switch_to.window(main_window)
                        
                    except Exception as house_error:
                        print(f"❌ 处理房源时出错: {house_error}")
                        try:
                            driver.switch_to.window(main_window)
                        except:
                            pass
                        continue
                
                # 快速翻页
                if i < 32:
                    try:
                        next_btn = driver.find_element(By.XPATH, '//a[contains(text(), "下一页")]')
                        driver.execute_script("arguments[0].click();", next_btn)  # 使用JS点击，更快
                        time.sleep(0.5)  # 减少翻页等待时间
                        print(f"✅ [{area_name}] 快速翻页到第{i+1}页")
                    except Exception as page_error:
                        print(f"❌ 翻页失败: {page_error}")
                        if switch_proxy_simple(i+1, area_url):
                            continue
                        else:
                            break
                            
            except Exception as page_error:
                print(f"❌ 第{i}页处理失败: {page_error}")
                if not switch_proxy_simple(i, area_url):
                    break
                    
        print(f"📊 [{area_name}] 区域完成，共采集 {area_result_count} 条数据")
        
    except Exception as area_error:
        print(f"❌ 区域 [{area_name}] 处理失败: {area_error}")
        switch_proxy_simple(1, None)
        continue

# 保存数据
quit_flag = True
print(f"🎉 爬取完成！共采集了 {len(result_list)} 条房源数据")

if result_list:
    try:
        df = pd.DataFrame(result_list)
        df.to_excel('lianjia_data_areas_complete.xlsx', index=False)
        print(f"✅ 数据已保存到: lianjia_data_areas_complete.xlsx")
        
        # 统计各区域数据
        area_stats = {}
        for item in result_list:
            area = item.get('区域', '未知')
            area_stats[area] = area_stats.get(area, 0) + 1
        
        print(f"📈 各区域数据统计:")
        for area, count in area_stats.items():
            print(f"   - {area}: {count} 条")
            
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")

print("🎉 程序结束")
driver.quit()
