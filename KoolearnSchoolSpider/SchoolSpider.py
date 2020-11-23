import requests
import bs4
import openpyxl
import re


# 抓取整个页面
def get_url(url):
    # headers = [
    #     {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    #     {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 '
    #                    'Safari/535.11'},
    #     {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
    res = requests.get(url, headers=headers)

    return res


# 获取页数
def get_depth(res):
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    # 通过末页链接获取最大页数
    last_page = soup.find('a', text='末页')
    depth = re.search(r'(p=)(\d+)', str(last_page))

    return int(depth.group(2))  # 返回匹配中第二组结果, 即数字部分


# 提取搜索页基本院校信息
def find_school_basic_data(res):
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    name = []
    school_type = []
    attribute = []
    built_time = []
    location = []
    school_url = []
    info = []

    # 提取学校名称
    # find_all( name , attrs , recursive , text , **kwargs )
    untreated_title = soup.find_all('a', class_='green st')
    # find_all() 方法返回全部的搜索结构
    for each in untreated_title:
        name.append(each.text)
        each_url = re.search(r'href="(.+?)"', str(each))  # (.+?) 为非贪婪模式
        school_url.append(each_url.group(1))

    # 提取所在城市
    untreated_location = soup.find_all('p', class_='w_60', text=re.compile('所在城市：'))
    for each in untreated_location:
        location.append(str(each.text).replace('所在城市：', ''))

    # 提取院校类型
    untreated_type = soup.find_all('p', class_='w_60', text=re.compile('院校类型：'))
    for each in untreated_type:
        school_type.append(str(each.text).replace('院校类型：', ''))

    # 提取院校属性
    untreated_attribute = soup.find_all('p', text=re.compile('院校属性：'))
    for each in untreated_attribute:
        attribute.append(str(each.text).replace('院校属性：', ''))

    # 提取建校时间
    untreated_built_time = soup.find_all('p', text=re.compile('建校时间：'))
    for each in untreated_built_time:
        built_time.append(str(each.text).replace('建校时间：', ''))

    # 整合数据
    for i in range(0, len(name)):  # 从 1 开始, 第 0 列为列名
        info.append([name[i], location[i], school_type[i],
                     attribute[i], built_time[i], school_url[i]])
        # print(info[i])  # 测试
    # info.insert(0, ['院校名称', '所在城市', '院校类型', '院校属性', '建校时间', 'URL'])  # 插入列名
    return info


# 提取院校页面中院校首页的详细信息
def find_school_home_page(res):
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    # 提取院校名称
    name = soup.find('h3', class_='f_l').text
    # print(name)

    # 提取院校代码
    code = str(soup.find('p', class_='f_l').text).replace('院校代码', '')
    # print(code)

    # 提取所属省份
    province = str(soup.find('span', class_='first').text).replace('所属省份：', '')
    # print(province)

    # 提取所属分区
    regional = str(soup.find('span', class_='sec').text).replace('所属分区：', '')
    # print(regional)

    # 提取院校性质
    nature = str(soup.find('span', class_='thr').text).replace('院校性质：', '')
    # print(nature)

    # 提取院校类型
    """
    find_all() 返回的结果是一个列表
    """
    school_type = str(soup.find_all('span', class_='first', text=re.compile('院校类型：'))[0].text).replace('院校类型：', '')
    # print(school_type)

    # 提取院校排名
    ranking = str(soup.find_all('span', class_='sec', text=re.compile('院校排名：'))[0].text).replace('院校排名：', '')
    # print(ranking)

    # 提取院校属性
    attribute = str(soup.find_all('span', class_='thr', text=re.compile('院校属性：'))[0].text).replace('院校属性：', '')
    # print(attribute)

    # 提取地区竞争力排行
    area_competitive = str(soup.find('span', class_='four').text).replace('考研地区竞争力排行：', '')
    # print(area_competitive)

    # 提取院校竞争力排行
    school_competitive = str(soup.find_all('span', text=re.compile('研究生院竞争力排行：'))[0].text).replace('研究生院竞争力排行：', '')
    # print(school_competitive)

    # 提取联系方式
    phone_number = str(soup.find('p', class_='mb3').text).replace('联系方式：', '')
    # print(phone_number)

    # 提取院校图片链接
    img_url = 'http://college.koolearn.com/upload/school/kaoyan/' + code + '.jpg'
    # print(img_url)

    # 整合数据
    detail_info = [name, code, province, regional, nature, school_type, ranking,
                   attribute, area_competitive, school_competitive, phone_number, img_url]

    return detail_info


# 提取院校简介
def find_school_introduction(res):
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    info = soup.find('div', class_='sch_intro blu f_l')
    article = info.find_all(text=re.compile(r"[\u4e00-\u9f5a]+"))  # 匹配含有中文字符的字段

    if len(article) > 1:
        result = article[1]  # [0] 是 xx大学简介几个字
    else:
        result = article[0]

    return result


# 导出数据
def data_export(data):
    # 导出院校基本信息表
    wb = openpyxl.Workbook()  # 坑爹, Workbook() 的 W 要大写
    wb.guess_types = True  # 自动匹配数据类型
    ws = wb.active
    # ws.append(['院校名称', '所在城市', '院校类型', '院校属性', '建校时间', 'URL'])  # 列名
    for each in data:
        ws.append(each)

    wb.save('院校详细信息.xlsx')


def main():
    school_basic_url = 'http://college.koolearn.com/kaoyan/s/yx-0-0-0-0-0-0/?p='
    school_basic_res = get_url(school_basic_url + '0')
    school_basic_info = find_school_basic_data(school_basic_res)
    depth = get_depth(school_basic_res)
    for i in range(1, depth):  # 0之前已经包含, 从1开始
        school_basic_res = get_url(school_basic_url + str(i))
        school_basic_info += find_school_basic_data(school_basic_res)

    # print(school_basic_info)
    # 调用提取院校详细信息
    school_detail_info = []
    for i in range(0, len(school_basic_info)):  # 从 1 开始, 第 0 列为列名
        school_detail_url = school_basic_info[i][5]
        # print(school_detail_url)
        school_introduction = find_school_introduction(get_url(school_detail_url + 'about/'))
        # print(school_introduction)
        all_info = find_school_home_page(get_url(school_detail_url))
        all_info.append(school_introduction)
        # print(all_info)`
        school_detail_info.append(all_info)
        # print(school_detail_info)
    # school_detail_info.insert(0, ['院校名称', '院校代码', '所属省份', '所属分区', '院校性质', '院校类型', '院校排名', '院校属性',
    #                               '地区竞争力排行', '院校竞争力排行', '联系方式', '院校图片链接', '院校简介'])

    # data_export(school_basic_info)
    data_export(school_detail_info)
    # 打印测试数据
    # with open('school.txt', 'w', encoding='utf-8') as file:
    #     file.write(school_basic_res.text)


if __name__ == '__main__':
    main()
