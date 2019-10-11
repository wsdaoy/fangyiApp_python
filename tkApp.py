from tkinter import *
import tkinter.messagebox
import threading
import requests,time,random,lxml,re,gc
from bs4 import BeautifulSoup
from retrying import retry


def make_md5(needMD5):
    import hashlib
    
    md5_o = hashlib.md5()   # 实例化md5对象
    string = needMD5.encode('utf-8')  #编码转化为utf-8格式
    md5_o.update(string)    # 更新md5 object的值
    sign_str = md5_o.hexdigest()
    return sign_str  #返回加密后的字符串

def make_request_data(needFYdata,needFYtype):
    global reqTypeMakeDict,temp_postfix
    newDict = dict(zip(reqTypeMakeDict.values(),reqTypeMakeDict.keys()))   #键值互换
    # form 的生成1. i 需要确定, 2, salt, 3, sign
    needFYdata.encode('utf-8')
    r = int(time.time()*1000)  #匹配时间戳
    salt_str = '{}{}'.format(r, random.randint(0,9))  #salt的js破解
    # print(salt_str)
    
    # sign_postfix = 
    sign_str = "fanyideskweb" + needFYdata + salt_str + temp_postfix  #sign的js破解
    sign_md5_str = make_md5(sign_str)   # 上面的字符串传入进行md5加密
    
    browserVersion_str = '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    browserVersion_md5_str = make_md5(browserVersion_str)
    #发送的表单信息
    type_from = 'AUTO'
    type_to = 'AUTO'
    if needFYtype:
        index = re.search("2",needFYtype,re.S).span()[0]
        type_from = needFYtype[:index]
        type_to = needFYtype[index+1:]
    formData = {
        'i':needFYdata,
        'from': type_from,
        'to': type_to,
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': salt_str,
        'sign': sign_md5_str,
        'ts': str(r),
        'bv': browserVersion_md5_str,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME'
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '251',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'OUTFOX_SEARCH_USER_ID_NCOO=1321392558.1546452; OUTFOX_SEARCH_USER_ID="-1182898728@10.169.0.83"; JSESSIONID=aaakPDVwl0CWSaTx5pPTw; ___rl__test__cookies={}'.format(r),
        'Host': 'fanyi.youdao.com',
        'Origin': 'http://fanyi.youdao.com',
        'Referer': 'http://fanyi.youdao.com/',
        'User-Agent': r'Mozilla/'+browserVersion_str,
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    return formData,headers
    
def request_fanyi_data(needFYdataFunction):
    url ='http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    
    formData,headers = needFYdataFunction

    rt = requests.post( url , data=formData , json=True , headers=headers)
    # text=rt.content  #二进制数据
    response = rt.json()
    return response  #返回json数据


class appIndex_box:  #界面类
    
    ListboxToWindow = True

    def __init__(self):# 类的“初始变量”
        self.rootindex = Tk()
        self.rootindex.title('翻译软件')
        sw = self.rootindex.winfo_screenwidth()   #获取屏幕宽度
        sh = self.rootindex.winfo_screenheight()  #获取屏幕高度
        # print(sw,sh)
        x = int(sw-400)
        y = int(sh-600)
        # print(x,y)
        # self.rootindex.attributes('-alpha',0.8)
        # self.rootindex.overrideredirect(True)
        self.rootindex.geometry('340x520+{}+{}'.format(x,y))   #固定窗口位置
        self.result = ''
        self.historyData = [""]
        self.showLongText = True
        # print(self.result)
        self.FYtypeBtn_str = StringVar()
        self.FYtypeBtn_str.set('自动检测')
        self.longTextBtn_str = StringVar()
        self.longTextBtn_str.set('长文本')
        self.needFYtype = ''
        self.changeFYtype = False

    def __FYresult_operation_box(self):
        global reqTypeMakeDict
        if self.showLongText:
            value = self.t1.get()
        else:
            value = self.t1.get("1.0", END)
        if value != self.historyData[-1] or self.changeFYtype:  #判断是否需要请求

            getFYData = request_fanyi_data(make_request_data(value,self.needFYtype))  #请求返回的数据
            if 'type' in getFYData:
                self.FYtypeBtn_str.set(reqTypeMakeDict[getFYData['type']])   #翻译结果类型
                self.t3.delete("1.0",END)
                self.t3.pack_forget()
                self.rootindex.update()
                if 'smartResult' in getFYData:   #其余的返回值
                    smartResult = getFYData['smartResult']['entries']
                    for i in smartResult:
                        iend = re.sub(r'\r\n','',i,re.S)
                        if iend:
                            self.t3.insert(INSERT,iend)
                            self.t3.insert(INSERT,'\n')
                        self.rootindex.update()
                        self.t3.pack()

            if getFYData['errorCode'] == 0:
                self.t2.delete("1.0",END)
                rquestMsg = getFYData['translateResult'][0][0]['src']
                getFYfinishData = getFYData['translateResult'][0][0]['tgt']
                dataType = getFYData['type']
                self.t2.insert(INSERT, getFYfinishData)

            self.changeFYtype = False
            self.historyData.append(value)  #保存历史值
        
    def FYtext_button(self):
        self.__FYresult_operation_box()  #翻译按钮完成函数

    def __FYtext_button(self,event):
        self.__FYresult_operation_box()  #翻译按钮完成函数

    def __copytext_button(self):
        result = self.t2.get("1.0",END)
        result = re.sub(r'\n','',result,re.S)  #去除回车
        self.t2.clipboard_clear()  #清除上一个复制
        self.t2.clipboard_append(result)
        # self.t2.event_generate("<<Copy>>")
        i = 0
        # print(result)
        while i < 10 and result:   #复制提醒弹窗（减少线程占用造成卡顿）
            self.message.pack(ipadx=15.0, ipady=5.0)
            self.rootindex.update()
            self.rootindex.after(120, self.message.pack_forget())  #移除控件
            i += 1

    def listbox_index(self):
        global boxListData,boxListDataLen
        
        # if self.ListboxToWindow:
        self.listbox_index = Tk()
        self.listbox_index.geometry('150x350+1240+430')
        # self.listbox_index.attributes('-alpha',0.8)
        self.listbox_index.overrideredirect(True)
        self.theLB = Listbox(self.listbox_index, width=30, height=boxListDataLen, font=('黑体', 12),
                exportselection=False)
        self.theLB.pack()
        for item in boxListData:
            self.theLB.insert("end", item)
        self.listbox_index.update()
        self.listbox_index.bind('<Button-1>',self.__touch_listbox_item)
        self.listbox_index.mainloop()

    def __touch_listbox_item(self,event):  #点击listBOX绑定事件
        global boxListData,reverse_reqTypeMakeDict
        self.listbox_index.update()
        DictKey = boxListData[self.theLB.curselection()[0]]
        self.needFYtype = reverse_reqTypeMakeDict[DictKey]
        self.changeFYtype = True
        self.FYtypeBtn_str.set(DictKey)  #选中的字符串
        self.__FYresult_operation_box()
        time.sleep(0.3)
        self.listbox_index.destroy()
        
    def longText_mode(self):
        if self.showLongText:
            self.t1.pack_forget()
            self.t1.update()
            self.t1 = Text(self.fm1, font=('黑体', 16), width=26, height=5, borderwidth=2)
            self.t1.update()
            self.t1.pack(side='left',anchor='n')
            self.longTextBtn_str.set("短文本")
            self.showLongText = False
        else:
            self.t1.pack_forget()
            self.t1.update()
            self.t1 = Entry(self.fm1, font=('黑体', 16), width=26, borderwidth=2)
            self.t1.update()
            self.t1.pack(side='left',anchor='n',ipady=3.0)
            self.longTextBtn_str.set("长文本")
            self.showLongText = True

    def _onclickRbtn(self,event):    #右键菜单
        menu = Menu(self.rootindex, tearoff=0)
        menu.add_command(label="复制", command=self.onCopy)  #右键按钮
        menu.add_separator()  #横线
        menu.add_command(label="粘贴", command=self.onPaste)
        menu.add_separator()
        menu.add_command(label="剪切", command=self.onCut)
        menu.post(event.x_root, event.y_root)
        # print(event)

    def onPaste(self):
        try:
            text = self.rootindex.clipboard_get()
        except TclError:
            pass
        # print('onPaste',text)
        self.t1.insert(INSERT,text)
 
    def onCopy(self):
        try:
            self.text = self.t2.get('sel.first', 'sel.last')
        except:
            self.text = ''
        if(not self.text):
            try:
                self.text = self.t3.get('sel.first', 'sel.last')
            except:
                pass
        self.rootindex.clipboard_clear()    #以免多次copy
        self.rootindex.clipboard_append(self.text)
        # print('onCope',self.text)
 
    def onCut(self):
        self.onCopy()  #复制后清除
        try:
            self.t2.delete('sel.first', 'sel.last')
        except TclError:
            pass
    
    def history_show_box(self,e):    #历史记录
        boxListDataLen = len(self.historyData)
        toproot = Toplevel()
        toproot.title("查看历史记录")
        theLB = Listbox(toproot, width=30, height=boxListDataLen, font=('黑体', 12),
                exportselection=False, selectmode="SINGLE")
        theLB.insert("end","暂时无数据")
        for item in self.historyData:
            if item:
                theLB.insert("end", item)
        theLB.pack(ipadx=5.0, ipady=5.0)
        toproot.update()
        # toproot.bind('<Button-1>',self.__touch_listbox_item)
        print(self.historyData)

    def indexButton(self):  # 组件使用
        historyIcon = PhotoImage(file="软件/有道/image/lishi.png")
        fm0 = Frame(self.rootindex)
        self.fm1 = Frame(self.rootindex)
        l1 = Label(fm0,text='你可能需要翻译：',font=('幼圆', 14), fg="#666666" )
        l2_img = Label(fm0,image=historyIcon, width=32, height=32)
        self.t1 = Entry(self.fm1, font=('黑体', 16), width=26, borderwidth=2)
        self.t2 = Text(self.rootindex, font=('幼圆', 16), width=30, height=3)
        self.t3 = Text(self.rootindex, font=('幼圆', 15), width=30, height=4)
        b1 = Button(self.rootindex, text='翻译', width=15, height=2, bg='#7FFF00', command=self.FYtext_button)
        b2 = Button(self.rootindex, text='复制', width=15,height=2, command=self.__copytext_button)
        b3 = Button(self.rootindex, textvariable=self.FYtypeBtn_str, width=40,height=2, bg='#ffbb00', command=self.listbox_index)
        b4 = Button(self.fm1, textvariable=self.longTextBtn_str, width= 5, height=1, command=self.longText_mode)
        self.message = Message(self.rootindex, font=('黑体', 9) , text='文本已复制', width=100, bg='#777777', fg='#ffffff')
        #右键菜单
        self.rootindex.bind("<Button-3>", self._onclickRbtn)
        self.rootindex.bind("<Return>",self.__FYtext_button)
        l2_img.bind("<Button-1>",self.history_show_box)
        #组件定位
        l1.pack(pady=3.0,anchor='n',side='left')
        l2_img.pack(padx=10.0,pady=5.0,anchor="n",side='right')
        fm0.pack(anchor="w",fill = X)
        self.t1.pack(side='left',anchor='n',ipady=3.0)
        b4.pack(side='right',anchor='n')
        self.fm1.pack(pady=10.0)
        b1.pack(pady=5.0)
        b2.pack(pady=5.0)  #,anchor='e'
        self.t2.pack(ipady=10.0)
        b3.pack(pady=30.0)  #,anchor='e'
        
        self.rootindex.mainloop()

def startPage_thread():
    global startPage,L1
    startPage = Tk()
    startPage.title('启动页面')
    sw = startPage.winfo_screenwidth()   #获取屏幕宽度
    sh = startPage.winfo_screenheight()  #获取屏幕高度
    # print(sw,sh)
    x = int(sw-350)
    y = int(sh-520)
    # print(x,y)
    # self.rootindex.attributes('-alpha',0.8)
    # self.rootindex.overrideredirect(True)
    startPage.geometry('300x150+{}+{}'.format(x,y))   #固定窗口位置
    L1 = Label(startPage,text='程序启动中。。。',font=('黑体', 14))
    L1.pack(padx=25.0,pady=50.0)
    startPage.after(2000,close_startPage)
    # startPage.bind("<Return>",close_startPage)
    startPage.mainloop()

def close_startPage():
    global startPage
    L1.pack_forget()
    startPage.destroy()
    del startPage
    gc.collect()
    print("关闭")

def startReq_jsData():
    global temp_postfix
    temp_request = requests.get("http://shared.ydstatic.com/fanyi/newweb/v1.0.18/scripts/newweb/fanyi.min.js").text
    search_string = re.compile(r'sign\:n\.md5\(\"fanyideskweb\"\+e\+i\+\"(.*?)\"\)\}\}',flags = re.S)
    temp_postfix = search_string.findall(temp_request)[0]
    #请求翻译结果的类型
    first_request_language_type()

@retry(stop_max_attempt_number = 5, stop_max_delay =3000)
def first_request_language_type(): #获取语言种类
    global reqTypeMakeDict,boxListData,boxListDataLen,reverse_reqTypeMakeDict
    url = "http://fanyi.youdao.com"
    r = int(time.time()*1000)  #匹配时间戳
    headers = {
        'Accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': r'OUTFOX_SEARCH_USER_ID_NCOO=1321392558.1546452; OUTFOX_SEARCH_USER_ID="-1182898728@10.169.0.83"; _ntes_nnid=b6f6d344118b9c9a876fe3e6d13d92a3,1560844609165; JSESSIONID=aaarWNkEpNuzAbl7KVTTw; ___rl__test__cookies={}'.format(r),
        'Host': 'fanyi.youdao.com',
        'Referer': r'http://fanyi.youdao.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    request_url = requests.get(url, headers=headers)
    if request_url.status_code == 200:
        html = str(request_url.text)
        soup = BeautifulSoup(html,'lxml')
        lis = soup.select('#languageSelect')[0].select('li')
        lis.pop(0)
    for li in lis:
        value = re.sub(r'\xa0','',li.text,flags=re.S)
        reqTypeMakeDict[li['data-value']] = value
        reverse_reqTypeMakeDict[value] = li['data-value']
    boxListData = list(reqTypeMakeDict.values())
    boxListData.sort(reverse=False)
    boxListDataLen = len(boxListData)


def main():   #主函数
    #设置次级线程，更新数据，提升使用流畅性
    pageThread = threading.Thread(target=startPage_thread, )
    reqDataThread = threading.Thread(target=startReq_jsData, )   #获取混入加密的数据段
    reqDataThread.start()   #启动线程1

    pageThread.setDaemon(True)   #设置为守护线程
    pageThread.start()   #启动线程2
    pageThread.join()   #等待该线程完成
    
    gc.collect()    #数据垃圾回收
    #软件主界面
    appindex = appIndex_box()
    appindex.indexButton()
    

if __name__ == '__main__':
    #定义全局变量，需用global引用
    reqTypeMakeDict = {}  #初次请求类型返回事件字典
    reverse_reqTypeMakeDict = {}   #字典键值互换
    boxListData = []
    boxListDataLen = 0
    temp_postfix = ''
    startPage = object()
    #定义初始线程
    
    #引用函数
    main()    #运行主线程代码