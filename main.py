from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome()

service = Service()

url = "https://sh.lianjia.com/ershoufang/"

driver.get(url)


result_list = []
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
        
        main_window = driver.current_window_handle
        
        driver.execute_script(f"window.open('{href}');")
        
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
            property_type = driver.find_element(By.CSS_SELECTOR,'div.area > div.subInfo.noHidden').text.strip()
            match = re.match(r'(\d{4})年建/(.+)', property_type)
            if match:
                data_dict['年份'] = match.group(1)
                data_dict['房子类型'] = match.group(2)
            else:
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

        try:
            if new_window and len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(main_window)
        except Exception as e:
            print(f"窗口切换异常: {e}")
            try:
                driver.switch_to.window(main_window)
            except:
                pass
       
    try:
        next_page_btn = driver.find_element(By.XPATH, '//a[contains(text(), "下一页")]')
        next_page_btn.click()
        time.sleep(0.6)
    except Exception as e:
        print('未找到下一页，或已到最后一页')
        break

print(result_list)

df = pd.DataFrame(result_list)

df.to_excel('lianjia_data.xlsx', index=False)

driver.quit()