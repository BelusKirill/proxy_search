from bs4 import BeautifulSoup as bs
from threading import Thread

import PySimpleGUI as sg
import pyperclip
import requests
import time

count = 0
countgood = 0
countbat = 0
countall = 0
count_target_proxy = 0
flag_get_proxy = True

def get_proxys(select_combo):
    url = ''
    proxy = []
    proxys = []
    type_proxy = ''

    if select_combo == 'sslproxies': 
        url = 'https://www.sslproxies.org/'
        type_proxy = 'ssl'
    elif select_combo == 'socks-proxy':
        url = 'https://www.socks-proxy.net/'
        type_proxy = 'socks'

    try:
        r = requests.get(url)
    except Exception as ex:
        print(ex)
        return [-1, ex]

    print(r.status_code)

    soup = bs(r.text, "html.parser")
    element = soup.find('div', 'table-responsive fpl-list')
    element = element.find('tbody')
    elements = element.find_all('td')

    if type_proxy == 'socks':
        index = 0
        for item in elements:
            if index == 0:
                proxy.append(item.text)
            if index == 1:
                proxy.append(item.text)
            if index == 3:
                proxy.append(item.text)
            if index == 4:
                proxy.append(item.text)
            elif index == 7:
                proxy.append(item.text)
                proxys.append(proxy[:])
                proxy.clear()
                index = -1
            index += 1
    elif type_proxy == 'ssl':
        index = 0
        for item in elements:
            if index == 0:
                proxy.append(item.text)
            if index == 1:
                proxy.append(item.text)
            if index == 3:
                proxy.append(item.text)
            if index == 6:
                proxy.append('Https' if item.text == 'yes' else 'Http')
            elif index == 7:
                proxy.append(item.text)
                proxys.append(proxy[:])
                proxy.clear()
                index = -1
            index += 1

    return type_proxy, proxys

def check_one_proxy(proxy, url,headers, table):
    global count
    global countgood
    global countbat
    global countall
    global count_target_proxy
    proxies = {}

    if (proxy[3]=='https' or proxy[3]=='http'):
        proxies = {
            'https': f'{proxy[0]}:{proxy[1]}',
            'http': f'{proxy[0]}:{proxy[1]}',
        }
    elif (proxy[3]=='socks4'):
        proxies = {
            'https': f'socks4://{proxy[0]}:{proxy[1]}',
            'http': f'socks4://{proxy[0]}:{proxy[1]}',
        }
    elif (proxy[3]=='socks5'):
        proxies = {
            'https': f'socks5://{proxy[0]}:{proxy[1]}',
            'http': f'socks5://{proxy[0]}:{proxy[1]}',
        }

    if url == '':
        url = 'https://2ip.ru/'

    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=15)
        #print(response.status_code)
        html = response.text
        if url == 'https://2ip.ru/':
            soup = bs(html, "lxml")
            temp = soup.find(id="d_clip_button").text
        #if proxy[0] == temp:
        proxy[4] = response.elapsed.total_seconds()
        data = table.get()[:]
        data.append(proxy)
        table.update(values=data)
        countgood += 1
    except Exception as ex:
        #print(ex)
        countbat += 1
    finally:
        count += 1
        count_target_proxy -= 1

def count_target_1(count_target_1, stat):
    global count
    global countgood
    global countbat
    global countall
    global count_target_proxy

    count = 0
    countgood = 0
    countbat = 0
    count_target_proxy = 0

    while(True):
        count_target_1.update(f'??????????????: {count_target_proxy}')
        stat.update(f'????????????????????: {count}, ??????????????: {countgood}, ????????????: {countbat}, ??????????: {countall}, ????????????????: {countall-count}')
        time.sleep(1)

def check_proxy(proxys, url, table, btn):
    global count
    global countgood
    global countbat
    global countall
    global count_target_proxy
    global flag_get_proxy

    count = 0
    countgood = 0
    countbat = 0
    count_target_proxy = 0
    countall = len(proxys)

    i = 0
    headers={"User-Agent": "Opera/9.80 (X11; Linux x86_64; U; de) Presto/2.2.15 Version/10.00"}
    for proxy in proxys[:]:
        while(True):
            if count_target_proxy < 30:
                if flag_get_proxy == False:
                    if count_target_proxy == 0:
                        break
                    else:
                        continue

                time.sleep(0.2)
                count_target_proxy += 1
                th = Thread(target = check_one_proxy, args=(proxy, url, headers, table,))
                th.start()
                break
            else:
                time.sleep(1)
    
    btn.update(disabled=False)
    flag_get_proxy = True
    return

sg.theme('DarkAmber')

layout_column = [[sg.Text('???????????? ?????? ????????????????'), sg.InputText(key='-IN-')],
                [sg.Table(values = [],
                          key='-TABLE-', 
                          headings=['Id', 'Port', 'Country', 'Type', 'Last Checked'],
                          col_widths=[20, 10, 10, 6],
                          pad=(25,25), 
                          display_row_numbers=True, 
                          auto_size_columns=False, 
                          enable_events=True)]]

layout_column2 = [[sg.Table(values = [],
                key='-TABLE2-', 
                headings=['Id', 'Port', 'Country', 'Type', 'Speed'],
                col_widths=[20, 10, 10, 6],
                pad=(25,25), 
                display_row_numbers=True, 
                auto_size_columns=False, 
                enable_events=True)],
                [sg.Text(key='-STAT-')],
                [sg.Text(key='-count_target_1-')]]

COMBO = ['sslproxies', 'socks-proxy', 'choice 3']

layout_tab1 = [[sg.Text('????????????????????: '), sg.Button('id:port', key='-BTNcopy-')],
        [sg.Text('??????????????: '), 
        sg.Combo(COMBO,
            default_value=COMBO[0], 
            enable_events=True, 
            key='-COMBO-',
            readonly =True), 
        sg.Button('???????????????? ????????????', key='-GETproxy-'),
        sg.Button('?????????????????? ????????????', key='-CHECKproxy-')],
        [sg.Text('??????: '), sg.Text('',  key='-TYPEproxy-')],
        [sg.Text(text='Error', text_color='red', visible=False, key='-TEXT_ERR-', enable_events=True, size=[69,3])],
        [sg.Column(layout_column, element_justification='center')]]

layout_tab2 = [[sg.Text('????????????????????: '), sg.Button('id:port', key='-BTNcopy2-')],
                [sg.Text('??????????????: '), sg.Button('????????', key='-BTNstop-')],
                [sg.Column(layout_column2, element_justification='center')]]

TABGroup = [[sg.Tab('Tab 1', layout_tab1, key='-TAB1-'), 
            sg.Tab('Tab 2', layout_tab2, key='-TAB2-')]]


layout = [[sg.TabGroup(TABGroup, selected_title_color='green', pad=(0,0), key='-TABGroup-', enable_events=True)]]

# Create the Window
window = sg.Window('????????????', layout, finalize=True, margins=(0,0))
table = window['-TABLE-']
table.bind('<Button-1>', 'Click')
table2 = window['-TABLE2-']
table2.bind('<Button-1>', 'Click')

th = Thread(target = count_target_1, args=(window['-count_target_1-'], window['-STAT-'],))
th.start()
# Event Loop to process "events"
while True:
    event, values = window.read()
    window['-TEXT_ERR-'].update(visible=False)
    window['-TEXT_ERR-'].hide_row()

    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == '-TABLE-':
        pass
    elif event == '-TABLE-Click':
        e = table.user_bind_event
        if e is not None:
            region = table.Widget.identify('region', e.x, e.y)
    elif event == '-BTNcopy-':
        e = table.user_bind_event
        if e is not None:
            region = table.Widget.identify('region', e.x, e.y)
            if region == 'cell':
                idexrow = int(table.Widget.identify_row(e.y))
                row = window['-TABLE-'].get()[idexrow-1]
                databuf = f"{row[0]}:{row[1]}"
                pyperclip.copy(databuf)
            else:
                continue
    elif event == '-BTNcopy2-':
        e = table2.user_bind_event
        if e is not None:
            region = table2.Widget.identify('region', e.x, e.y)
            if region == 'cell':
                idexrow = int(table2.Widget.identify_row(e.y))
                row = window['-TABLE2-'].get()[idexrow-1]
                databuf = f"{row[0]}:{row[1]}"
                pyperclip.copy(databuf)
            else:
                continue
    elif event == '-GETproxy-':
        select_combo = values['-COMBO-']
        type_proxy, proxys = get_proxys(select_combo)
        if (proxys is not None and type_proxy == -1):
            window['-TEXT_ERR-'].update(visible=True)
            window['-TEXT_ERR-'].update(value=proxys)
            window['-TEXT_ERR-'].unhide_row()
        else:
            window['-TABLE-'].update(values=proxys)
            window['-TYPEproxy-'].update(value=type_proxy)
    elif event == '-CHECKproxy-':
        data = window['-TABLE-'].get()
        window['-TABLE2-'].update(values = [])
        if data != []:
            url = window['-IN-'].get()
            window['-CHECKproxy-'].update(disabled=True)
            th = Thread(target = check_proxy, args=(data, url, window['-TABLE2-'], window['-CHECKproxy-']))
            th.start()
            window['-TAB2-'].select()
    elif event == '-BTNstop-':
        flag_get_proxy = False


window.close()