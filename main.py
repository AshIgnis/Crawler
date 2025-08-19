from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome()

service = Service()

url = "https://cc.lianjia.com/ershoufang/"

driver.get(url)


result_list = []
# 主循环，采集每一页
for i in range(1, 3):
    house_links = driver.find_elements(By.CSS_SELECTOR, 'ul.sellListContent li .title a')
    for element_link in house_links:
        data_dict = {
            "标题": "",
            "地区": "",
            "户型": "",
            "面积": "",
            "朝向": "",
            "装修": "",
            "楼层": "",
            "房子类型": "",
            "总价": "",
            "单价": "",
            "关注人数": "",
        }
        href = element_link.get_attribute('href')
        
        # 记录主窗口句柄
        main_window = driver.current_window_handle
        
        # 新开标签页
        driver.execute_script(f"window.open('{href}');")
        
        # 切换到新窗口
        new_window = None
        for handle in driver.window_handles:
            if handle != main_window:
                new_window = handle
                break
        
        if new_window:
            driver.switch_to.window(new_window)
            time.sleep(0.9)

        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.main').text.strip()
            data_dict['标题'] = title
        except:
            pass
        try:
            region = driver.find_element(By.CSS_SELECTOR, 'a.info').text.strip()
            data_dict['地区'] = region
        except:
            pass
        try:
            house_type = driver.find_element(By.CSS_SELECTOR,'div.room > div.mainInfo').text.strip()
            data_dict['户型'] = house_type
        except:
            pass
        try:
            area = driver.find_element(By.CSS_SELECTOR,'div.area > div.mainInfo').text.strip()
            data_dict['面积'] = area
        except:
            pass
        try:
            orientation = driver.find_element(By.CSS_SELECTOR,'div.type > div.mainInfo').text.strip()
            data_dict['朝向'] = orientation
        except:
            pass
        try:
            decoration = driver.find_element(By.CSS_SELECTOR,'div.type > div.subInfo').text.strip()
            data_dict['装修'] = decoration
        except:
            pass
        try:
            floor = driver.find_element(By.CSS_SELECTOR,'div.room > div.subInfo').text.strip()
            data_dict['楼层'] = floor
        except:
            pass
        try:
            property_type = driver.find_element(By.CSS_SELECTOR,'div.area > div.subInfo').text.strip()
            data_dict['房子类型'] = property_type
        except:
            pass
        try:
            total_price = driver.find_element(By.CSS_SELECTOR,'div.price span.total').text.strip()
            unit = driver.find_element(By.CSS_SELECTOR, 'div.price span.unit span').text.strip()
            data_dict['总价'] = total_price + unit
        except:
            pass
        try:
            unit_price = driver.find_element(By.CSS_SELECTOR,'div.unitPrice span.unitPriceValue').text.strip()
            data_dict['单价'] = unit_price
        except:
            pass
        try:
            followers = driver.find_element(By.CSS_SELECTOR, 'span#favCount').text.strip()
            data_dict['关注人数'] = followers
        except:
            pass

        result_list.append(data_dict)
        # 关闭详情页标签，切回主页面
        try:
            # 确保当前窗口存在且可以关闭
            if new_window and len(driver.window_handles) > 1:
                driver.close()
            # 切换回主窗口
            driver.switch_to.window(main_window)
        except Exception as e:
            print(f"窗口切换异常: {e}")
            # 确保回到主窗口
            try:
                driver.switch_to.window(main_window)
            except:
                pass
       
    # 翻页，找到"下一页"按钮
    try:
        next_page_btn = driver.find_element(By.XPATH, '//a[contains(text(), "下一页")]')
        next_page_btn.click()
        time.sleep(0.6)  # 等待新页面加载
    except Exception as e:
        print('未找到下一页，或已到最后一页')
        break

print(result_list)

df = pd.DataFrame(result_list)

df.to_excel('lianjia_data.xlsx', index=False)

driver.quit()