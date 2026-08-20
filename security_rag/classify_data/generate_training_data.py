"""
根据提示词模板生成5000条查询分类训练数据
- 通用知识: 2500条 (天气、时间、通用技术、日常闲聊、常识性问题等)
- 专业咨询: 2500条 (安保集团制度、执勤、押运、保险赔偿等专业问题)
"""
import json
import random
import os

random.seed(42)

# ===================== 通用知识模板 =====================
general_templates = [
    # 天气与时间
    ("今天天气怎么样？", "weather"),
    ("明天会下雨吗？", "weather"),
    ("现在几点了？", "time"),
    ("今天星期几？", "time"),
    ("北京今天的气温是多少？", "weather"),
    ("这周末天气好不好？", "weather"),
    ("上海明天冷不冷？", "weather"),
    ("今天适合出门吗？", "weather"),
    ("最近天气怎么变化这么大？", "weather"),
    ("冬天一般几点天黑？", "time"),
    ("夏天白天有多长？", "time"),
    ("今天是农历几号？", "time"),
    ("今年春节是几月几号？", "time"),
    ("国庆节放假几天？", "holiday"),
    ("中秋节什么时候？", "holiday"),
    ("清明假期怎么安排？", "holiday"),

    # 日常闲聊
    ("你好", "chat"),
    ("早上好", "chat"),
    ("在吗？", "chat"),
    ("你是谁？", "chat"),
    ("你能做什么？", "chat"),
    ("谢谢", "chat"),
    ("再见", "chat"),
    ("帮我讲个笑话吧", "chat"),
    ("今天心情不错", "chat"),
    ("好无聊啊", "chat"),
    ("有什么好看的推荐吗", "chat"),
    ("你觉得呢？", "chat"),
    ("真的假的？", "chat"),
    ("这也太难了吧", "chat"),
    ("有没有什么好玩的事情", "chat"),
    ("帮我写一段自我介绍", "chat"),
    ("帮我翻译一下谢谢", "chat"),
    ("你能帮我写邮件吗", "chat"),

    # 通用技术问题
    ("手机怎么连接WiFi？", "general_tech"),
    ("电脑开不了机怎么办？", "general_tech"),
    ("微信怎么发朋友圈？", "general_tech"),
    ("怎么设置手机闹钟？", "general_tech"),
    ("路由器怎么设置？", "general_tech"),
    ("打印机连不上怎么办？", "general_tech"),
    ("怎么清理手机内存？", "general_tech"),
    ("电脑太卡了怎么办？", "general_tech"),
    ("怎么恢复出厂设置？", "general_tech"),
    ("U盘读不出来怎么办？", "general_tech"),
    ("怎么把照片传到电脑上？", "general_tech"),
    ("蓝牙耳机怎么配对？", "general_tech"),
    ("怎么下载APP？", "general_tech"),
    ("密码忘了怎么办？", "general_tech"),
    ("怎么连接投影仪？", "general_tech"),
    ("Excel怎么求和？", "general_tech"),
    ("Word怎么设置页码？", "general_tech"),
    ("PPT怎么做动画效果？", "general_tech"),
    ("怎么把PDF转成Word？", "general_tech"),
    ("怎么截图？", "general_tech"),
    ("电脑蓝屏了怎么办？", "general_tech"),
    ("手机充电很慢怎么办？", "general_tech"),
    ("怎么设置开机密码？", "general_tech"),
    ("怎么卸载软件？", "general_tech"),
    ("文件打不开怎么办？", "general_tech"),
    ("怎么压缩文件？", "general_tech"),
    ("怎么共享文件夹？", "general_tech"),
    ("怎么连接打印机？", "general_tech"),
    ("怎么设置静态IP？", "general_tech"),
    ("怎么查看电脑配置？", "general_tech"),

    # 常识性问题
    ("中国的首都是哪里？", "common_sense"),
    ("地球有多大？", "common_sense"),
    ("水的化学式是什么？", "common_sense"),
    ("一年有多少天？", "common_sense"),
    ("光速是多少？", "common_sense"),
    ("人有多少颗牙齿？", "common_sense"),
    ("正常体温是多少度？", "common_sense"),
    ("一天要喝多少水？", "common_sense"),
    ("跑步有什么好处？", "common_sense"),
    ("感冒了怎么办？", "common_sense"),
    ("失眠怎么办？", "common_sense"),
    ("怎么提高记忆力？", "common_sense"),
    ("吃什么对眼睛好？", "common_sense"),
    ("高血压要注意什么？", "common_sense"),
    ("糖尿病能吃什么水果？", "common_sense"),
    ("怎么预防颈椎病？", "common_sense"),
    ("感冒和流感有什么区别？", "common_sense"),
    ("维生素C有什么作用？", "common_sense"),
    ("人为什么会打哈欠？", "common_sense"),
    ("为什么天空是蓝色的？", "common_sense"),
    ("为什么海水是咸的？", "common_sense"),
    ("彩虹是怎么形成的？", "common_sense"),
    ("为什么会地震？", "common_sense"),
    ("为什么会有四季变化？", "common_sense"),
    ("月亮为什么会变圆变缺？", "common_sense"),
    ("太阳有多大？", "common_sense"),
    ("恐龙为什么灭绝了？", "common_sense"),
    ("人为什么会做梦？", "common_sense"),
    ("人为什么要睡觉？", "common_sense"),
    ("为什么肚子会咕咕叫？", "common_sense"),

    # 数学计算
    ("计算 {a} + {b} 等于多少？", "math"),
    ("{a} 乘以 {b} 的结果是什么？", "math"),
    ("{a} 除以 {b} 等于多少？", "math"),
    ("计算 {a} - {b}", "math"),
    ("{a} 的平方是多少？", "math"),
    ("求 {a} 和 {b} 的最大公约数", "math"),
    ("{a} 的 {b} 次方是多少？", "math"),
    ("计算 √{a} 的值", "math"),
    ("{a} 除以 {b} 的余数是多少？", "math"),
    ("计算 {a}% 的 {b} 是多少", "math"),
    ("{a} 和 {b} 的最小公倍数是多少？", "math"),
    ("计算 {a} × {b} + {c}", "math"),
    ("{a} 的立方根是多少？", "math"),
    ("1到{a}的和是多少？", "math"),
    ("{a} 加 {b} 再乘以 {c} 等于多少？", "math"),

    # 通用概念
    ("什么是{concept}？", "concept"),
    ("解释一下{concept}的概念", "concept"),
    ("简述{concept}的原理", "concept"),
    ("{concept_a}和{concept_b}有什么区别？", "compare"),
    ("{concept_a}与{concept_b}的不同之处在哪里？", "compare"),
    ("请说明{concept}的工作原理", "concept"),
    ("什么是{concept}？举个例子", "concept"),
    ("解释{concept}的作用", "concept"),
    ("概述{concept}的核心思想", "concept"),
    ("为什么需要{concept}？", "concept"),
    ("{concept}有哪些应用场景？", "concept"),
    ("{concept}的优缺点是什么？", "concept"),

    # 生活常识
    ("怎么去除衣服上的油渍？", "life"),
    ("冰箱有异味怎么办？", "life"),
    ("怎么清洗空调滤网？", "life"),
    ("下水道堵了怎么办？", "life"),
    ("怎么消灭蟑螂？", "life"),
    ("衣服染色了怎么恢复？", "life"),
    ("怎么去除水垢？", "life"),
    ("皮鞋发霉了怎么办？", "life"),
    ("怎么快速解冻食物？", "life"),
    ("米饭煮夹生了怎么办？", "life"),
    ("怎么挑选西瓜？", "life"),
    ("怎么保存蔬菜更新鲜？", "life"),
    ("新铁锅怎么开锅？", "life"),
    ("怎么去除胶水痕迹？", "life"),
    ("白衣服发黄怎么洗白？", "life"),

    # ========== 噪声反例：使用与专业咨询相同关键词但明确是通用知识的条目 ==========
    # 天气类反例（防止模型把"天气"一律判为专业咨询）
    ("今天天气怎么样？", "weather_noise"),
    ("明天会下雨吗？", "weather_noise"),
    ("天气预报说明天下雨，是真的吗？", "weather_noise"),
    ("最近天气变化好大啊", "weather_noise"),
    ("今天气温多少度？", "weather_noise"),
    ("外面冷不冷？", "weather_noise"),
    ("今天适合出去运动吗？", "weather_noise"),
    ("夏天太热了怎么办？", "weather_noise"),
    ("冬天下雪路滑怎么开车？", "weather_noise"),
    ("暴雨天出门要带什么？", "weather_noise"),
    ("台风天怎么防护？", "weather_noise"),
    ("雾霾天戴口罩有用吗？", "weather_noise"),
    ("天气预报哪个APP比较准？", "weather_noise"),
    ("高温天气怎么防暑降温？", "weather_noise"),
    ("下雨天衣服怎么晾干？", "weather_noise"),
    ("下雪天怎么防止摔倒？", "weather_noise"),
    ("大雾天高速公路会封路吗？", "weather_noise"),
    ("天气预报的降水概率是什么意思？", "weather_noise"),
    ("为什么夏天下冰雹？", "weather_noise"),
    ("龙卷风是怎么形成的？", "weather_noise"),
    ("为什么冬天静电特别多？", "weather_noise"),
    ("湿度大对身体有什么影响？", "weather_noise"),
    ("紫外线强的时候怎么防晒？", "weather_noise"),
    ("天气预报中的风力等级怎么分？", "weather_noise"),
    ("沙尘暴天气怎么保护自己？", "weather_noise"),

    # 车辆类反例（防止模型把"车辆"一律判为专业咨询）
    ("私家车多久保养一次？", "vehicle_noise"),
    ("车辆保险怎么买比较划算？", "vehicle_noise"),
    ("车辆年检需要什么材料？", "vehicle_noise"),
    ("车辆违章怎么查询？", "vehicle_noise"),
    ("新车需要买哪些保险？", "vehicle_noise"),
    ("车辆保养去4S店还是外面修车店？", "vehicle_noise"),
    ("二手车过户需要什么手续？", "vehicle_noise"),
    ("车辆GPS定位器怎么安装？", "vehicle_noise"),
    ("车辆电瓶没电了怎么搭火？", "vehicle_noise"),
    ("车辆空调不制冷怎么办？", "vehicle_noise"),
    ("车辆轮胎气压多少合适？", "vehicle_noise"),
    ("车辆油耗突然增高是什么原因？", "vehicle_noise"),
    ("车辆刮擦了怎么报保险？", "vehicle_noise"),
    ("车辆泡水了怎么处理？", "vehicle_noise"),
    ("车辆怎么省油？", "vehicle_noise"),

    # 保险/赔偿类反例
    ("医疗保险怎么报销？", "insurance_noise"),
    ("车险理赔一般要多久？", "insurance_noise"),
    ("交通事故赔偿标准是什么？", "insurance_noise"),
    ("买了保险出险了怎么报案？", "insurance_noise"),
    ("人寿保险和意外险有什么区别？", "insurance_noise"),
    ("医疗保险报销比例是多少？", "insurance_noise"),
    ("车祸对方全责怎么索赔？", "insurance_noise"),
    ("保险到期了怎么续保？", "insurance_noise"),
    ("重疾险和医疗险哪个好？", "insurance_noise"),
    ("交通事故误工费怎么赔偿？", "insurance_noise"),
    ("房屋保险值得买吗？", "insurance_noise"),
    ("旅游保险怎么买？", "insurance_noise"),
    ("社保和商保有什么区别？", "insurance_noise"),
    ("保险免赔额是什么意思？", "insurance_noise"),
    ("快递丢了怎么赔偿？", "insurance_noise"),

    # 请假/考勤类反例
    ("请假条怎么写？", "leave_noise"),
    ("年假一般怎么安排？", "leave_noise"),
    ("请假扣工资合法吗？", "leave_noise"),
    ("病假需要什么证明？", "leave_noise"),
    ("调休和加班互换怎么算？", "leave_noise"),
    ("产假有多少天？", "leave_noise"),
    ("婚假怎么申请？", "leave_noise"),
    ("事假和病假哪个扣钱多？", "leave_noise"),
    ("迟到被扣工资合理吗？", "leave_noise"),
    ("加班费怎么计算？", "leave_noise"),

    # 口语化通用问题
    ("这个怎么弄？", "colloquial_general"),
    ("帮我查一下", "colloquial_general"),
    ("能不能讲讲？", "colloquial_general"),
    ("这是啥意思？", "colloquial_general"),
    ("咋回事啊？", "colloquial_general"),
    ("有没有人知道？", "colloquial_general"),
    ("不太懂这个", "colloquial_general"),
    ("能解释一下吗？", "colloquial_general"),
    ("有谁知道这个？", "colloquial_general"),
    ("请问一下", "colloquial_general"),
    ("想问一下", "colloquial_general"),
    ("不太明白", "colloquial_general"),
    ("这个是什么意思啊？", "colloquial_general"),
    ("有人了解吗？", "colloquial_general"),
    ("能帮忙看看吗？", "colloquial_general"),
]

# 用于填充概念模板的通用词汇
concepts = [
    "人工智能", "机器学习", "深度学习", "大数据", "云计算",
    "物联网", "区块链", "5G技术", "虚拟现实", "增强现实",
    "操作系统", "数据库", "计算机网络", "信息安全", "软件工程",
    "HTTP协议", "HTTPS协议", "TCP/IP协议", "DNS解析", "WiFi技术",
    "蓝牙技术", "NFC技术", "GPS定位", "传感器", "嵌入式系统",
    "Python", "Java", "JavaScript", "C++", "Go语言",
    "Linux", "Windows", "macOS", "Android", "iOS",
    "Docker", "Kubernetes", "微服务", "DevOps", "敏捷开发",
    "Redis", "MongoDB", "MySQL", "PostgreSQL", "Elasticsearch",
    "前端开发", "后端开发", "全栈开发", "移动开发", "游戏开发",
    "机器学习", "深度学习", "神经网络", "自然语言处理", "计算机视觉",
    "推荐系统", "知识图谱", "语音识别", "图像识别", "数据挖掘",
    "对称加密", "非对称加密", "数字签名", "数字证书", "防火墙",
    "云计算", "边缘计算", "量子计算", "并行计算", "分布式计算",
    "虚拟机", "容器", "Serverless", "函数计算", "API网关",
    "Session", "Cookie", "Token", "JWT", "OAuth2.0",
    "XSS攻击", "CSRF攻击", "SQL注入", "DDoS攻击", "中间人攻击",
    "数据清洗", "数据可视化", "数据分析", "数据建模", "数据挖掘",
    "Git", "SVN", "版本控制", "持续集成", "持续部署",
    "RESTful API", "GraphQL", "gRPC", "WebSocket", "RPC框架",
    "MapReduce", "Spark", "Hadoop", "Flink", "Hive",
]

concept_pairs = [
    ("TCP", "UDP"), ("HTTP", "HTTPS"), ("进程", "线程"),
    ("堆", "栈"), ("栈", "队列"), ("数组", "链表"),
    ("二叉树", "红黑树"), ("B树", "B+树"), ("MySQL", "PostgreSQL"),
    ("Redis", "Memcached"), ("MongoDB", "MySQL"), ("Docker", "虚拟机"),
    ("Kubernetes", "Docker"), ("Git", "SVN"), ("Session", "Cookie"),
    ("TCP的三次握手", "TCP的四次挥手"), ("GET请求", "POST请求"),
    ("面向对象", "面向过程"), ("前端", "后端"), ("算法", "数据结构"),
    ("编译", "解释"), ("深拷贝", "浅拷贝"), ("重载", "重写"),
    ("抽象类", "接口"), ("并行", "并发"), ("同步", "异步"),
    ("阻塞", "非阻塞"), ("值传递", "引用传递"), ("类", "对象"),
    ("继承", "组合"), ("聚合", "关联"), ("泛型", "反射"),
    ("机器学习", "深度学习"), ("监督学习", "无监督学习"),
    ("分类", "聚类"), ("回归", "分类"), ("CNN", "RNN"),
    ("BERT", "GPT"), ("LSTM", "GRU"), ("池化", "卷积"),
    ("云计算", "边缘计算"), ("虚拟机", "容器"),
    ("关系型数据库", "非关系型数据库"), ("TCP", "IP"),
    ("Java", "Python"), ("C++", "Java"), ("前端", "全栈"),
    ("Linux", "Windows"), ("iOS", "Android"), ("WiFi", "蓝牙"),
]

# ===================== 专业咨询模板 =====================
professional_templates = [
    # ========== 安保执勤相关 ==========
    # 勤务等级
    ("勤务等级分为哪几级？", "duty_level"),
    ("一级勤务和二级勤务有什么区别？", "duty_level"),
    ("什么情况下启动一级勤务？", "duty_level"),
    ("三级勤务的具体要求是什么？", "duty_level"),
    ("勤务等级调整的依据是什么？", "duty_level"),
    ("特级勤务期间有哪些注意事项？", "duty_level"),
    ("勤务等级和排班有什么关系？", "duty_level"),
    ("二级勤务需要增加巡逻频次吗？", "duty_level"),
    ("启动高等级勤务需要谁审批？", "duty_level"),
    ("勤务等级划分标准是什么？", "duty_level"),
    ("不同勤务等级的在岗人数要求一样吗？", "duty_level"),
    ("勤务等级提升后需要通知甲方吗？", "duty_level"),

    # 门卫值守
    ("门卫值守的主要职责是什么？", "gate_guard"),
    ("门卫值守需要注意哪些事项？", "gate_guard"),
    ("门卫登记流程是怎样的？", "gate_guard"),
    ("外来人员进入需要办理什么手续？", "gate_guard"),
    ("门卫发现可疑人员怎么处理？", "gate_guard"),
    ("门卫值守期间能离开岗位吗？", "gate_guard"),
    ("车辆进出需要怎么登记？", "gate_guard"),
    ("门卫交接班需要交接哪些内容？", "gate_guard"),
    ("门卫值守的着装要求是什么？", "gate_guard"),
    ("夜间门卫值守有什么特殊要求？", "gate_guard"),
    ("大件物品出入需要什么凭证？", "gate_guard"),
    ("门卫遇到不配合的人员怎么办？", "gate_guard"),
    ("访客登记需要记录哪些信息？", "gate_guard"),
    ("门卫岗位职责是什么？", "gate_guard"),
    ("门卫发现违禁物品怎么处理？", "gate_guard"),

    # 巡逻
    ("巡逻路线怎么规划？", "patrol"),
    ("巡逻间隔时间是多少？", "patrol"),
    ("巡逻时发现异常怎么处理？", "patrol"),
    ("夜间巡逻有什么注意事项？", "patrol"),
    ("巡逻打卡点怎么设置？", "patrol"),
    ("巡逻记录怎么填写？", "patrol"),
    ("电子巡更系统怎么使用？", "patrol"),
    ("巡逻中发现火灾隐患怎么办？", "patrol"),
    ("巡逻时需要携带哪些装备？", "patrol"),
    ("重点区域巡逻频次是多少？", "patrol"),
    ("两人巡逻编组有什么要求？", "patrol"),
    ("巡逻中遇到可疑物品怎么处理？", "patrol"),
    ("恶劣天气巡逻有什么调整？", "patrol"),
    ("停车场巡逻要注意什么？", "patrol"),
    ("楼顶和地下室巡逻多久一次？", "patrol"),

    # 交接班
    ("交接班流程是怎样的？", "handover"),
    ("交接班需要交接哪些内容？", "handover"),
    ("交接班记录表怎么填写？", "handover"),
    ("交接班时发现问题怎么处理？", "handover"),
    ("交接班迟到怎么处理？", "handover"),
    ("交接班可以不面对面交接吗？", "handover"),
    ("夜班和白班交接要注意什么？", "handover"),
    ("交接班时装备需要清点吗？", "handover"),
    ("交接班记录保存多长时间？", "handover"),
    ("交接班时甲方来检查怎么办？", "handover"),
    ("交班人员还没来接班人员能离开吗？", "handover"),
    ("交接班时发生突发事件怎么处理？", "handover"),

    # 突发事件
    ("遇到火灾怎么处理？", "emergency"),
    ("发现盗窃行为怎么办？", "emergency"),
    ("遇到暴力冲突怎么处理？", "emergency"),
    ("发生自然灾害时的应急预案是什么？", "emergency"),
    ("发现可疑包裹怎么处理？", "emergency"),
    ("有人闯入警戒区域怎么办？", "emergency"),
    ("遇到群体性事件怎么处理？", "emergency"),
    ("客户单位发生安全事故怎么办？", "emergency"),
    ("发现爆炸物怎么处理？", "emergency"),
    ("遇到劫持人质事件怎么办？", "emergency"),
    ("发生电梯困人事件怎么处理？", "emergency"),
    ("发现水管爆裂怎么办？", "emergency"),
    ("遇到停电怎么处理？", "emergency"),
    ("发生食物中毒事件怎么办？", "emergency"),
    ("发现燃气泄漏怎么处理？", "emergency"),
    ("遇到恐怖袭击威胁怎么办？", "emergency"),
    ("突发群体上访怎么处理？", "emergency"),
    ("发现有人坠楼怎么处理？", "emergency"),
    ("遇到交通事故怎么处理？", "emergency"),
    ("发生化学品泄漏怎么办？", "emergency"),

    # 考勤排班
    ("排班表多久出一次？", "scheduling"),
    ("排班可以调换吗？", "scheduling"),
    ("请假流程是怎样的？", "scheduling"),
    ("加班怎么计算？", "scheduling"),
    ("迟到早退怎么处理？", "scheduling"),
    ("考勤打卡方式是什么？", "scheduling"),
    ("调休怎么申请？", "scheduling"),
    ("节假日排班怎么安排？", "scheduling"),
    ("临时有事需要换班怎么办？", "scheduling"),
    ("病假需要提供什么证明？", "scheduling"),
    ("年假怎么计算？", "scheduling"),
    ("旷工怎么处理？", "scheduling"),
    ("每月工作时间是多少？", "scheduling"),
    ("三班倒怎么排班？", "scheduling"),
    ("考勤异常怎么处理？", "scheduling"),

    # 器材使用
    ("对讲机怎么使用？", "equipment"),
    ("执法记录仪怎么操作？", "equipment"),
    ("灭火器怎么使用？", "equipment"),
    ("防刺服怎么穿戴？", "equipment"),
    ("安检门怎么操作？", "equipment"),
    ("手持金属探测器怎么用？", "equipment"),
    ("监控设备怎么操作？", "equipment"),
    ("报警器怎么使用？", "equipment"),
    ("防暴盾牌怎么使用？", "equipment"),
    ("橡胶棍的使用规范是什么？", "equipment"),
    ("强光手电怎么使用？", "equipment"),
    ("器材损坏怎么报修？", "equipment"),
    ("器材丢失怎么处理？", "equipment"),
    ("装备日常保养怎么做？", "equipment"),
    ("对讲机频道怎么设置？", "equipment"),

    # 安检流程
    ("安检流程是怎样的？", "security_check"),
    ("安检发现违禁品怎么处理？", "security_check"),
    ("安检人员需要什么资质？", "security_check"),
    ("人身安检的步骤是什么？", "security_check"),
    ("行李安检的流程是什么？", "security_check"),
    ("车辆安检需要检查哪些部位？", "security_check"),
    ("安检设备的日常维护怎么做？", "security_check"),
    ("拒绝接受安检怎么处理？", "security_check"),
    ("液体安检怎么操作？", "security_check"),
    ("安检中发现管制刀具怎么办？", "security_check"),
    ("大型活动安检有什么特殊要求？", "security_check"),
    ("安检通道的设置标准是什么？", "security_check"),
    ("安检数据怎么统计上报？", "security_check"),

    # ========== 武装押运相关 ==========
    # 押运流程
    ("武装押运的基本流程是什么？", "escort_process"),
    ("押运前需要做哪些准备？", "escort_process"),
    ("押运任务一般几个人执行？", "escort_process"),
    ("押运路线怎么规划？", "escort_process"),
    ("押运到达后怎么交接？", "escort_process"),
    ("押运任务结束后需要做哪些工作？", "escort_process"),
    ("押运过程中能改变路线吗？", "escort_process"),
    ("押运前车辆检查包括哪些内容？", "escort_process"),
    ("押运任务的保密要求是什么？", "escort_process"),
    ("押运时需要携带哪些装备？", "escort_process"),
    ("押运前枪械检查怎么做？", "escort_process"),
    ("双人押运的分工是什么？", "escort_process"),
    ("押运任务的通讯要求是什么？", "escort_process"),
    ("押运过程中能停车吗？", "escort_process"),

    # 枪械管理
    ("枪械保管规定是什么？", "firearm"),
    ("领枪还枪的流程是什么？", "firearm"),
    ("枪械日常保养怎么做？", "firearm"),
    ("枪支弹药存放有什么要求？", "firearm"),
    ("枪弹库管理制度的内容是什么？", "firearm"),
    ("持枪证怎么办理？", "firearm"),
    ("枪支丢失怎么处理？", "firearm"),
    ("枪械故障怎么排除？", "firearm"),
    ("射击训练多久一次？", "firearm"),
    ("枪械使用安全规则是什么？", "firearm"),
    ("弹药领用规定是什么？", "firearm"),
    ("枪弹分离存放的要求是什么？", "firearm"),
    ("枪械保养记录怎么填写？", "firearm"),
    ("什么情况下可以使用武器？", "firearm"),
    ("使用武器的法律后果是什么？", "firearm"),

    # 车辆管理
    ("押运车辆日常检查包括什么？", "vehicle"),
    ("押运车辆的保养周期是多久？", "vehicle"),
    ("押运车辆发生故障怎么处理？", "vehicle"),
    ("车辆保险怎么办理？", "vehicle"),
    ("押运车辆的驾驶要求是什么？", "vehicle"),
    ("车辆GPS监控怎么使用？", "vehicle"),
    ("押运车辆的加油规定是什么？", "vehicle"),
    ("车辆清洁由谁负责？", "vehicle"),
    ("押运车辆能用于非押运任务吗？", "vehicle"),
    ("车辆年检和保养怎么安排？", "vehicle"),
    ("防弹运钞车的维护要求是什么？", "vehicle"),
    ("车辆违章怎么处理？", "vehicle"),
    ("押运车辆的停放规定是什么？", "vehicle"),
    ("车辆报废流程是什么？", "vehicle"),

    # 款箱交接
    ("款箱交接流程是什么？", "cash_box"),
    ("款箱交接需要核对哪些信息？", "cash_box"),
    ("款箱交接时发现数量不对怎么办？", "cash_box"),
    ("款箱交接需要双方签字吗？", "cash_box"),
    ("款箱损坏怎么处理？", "cash_box"),
    ("款箱交接的凭证是什么？", "cash_box"),
    ("款箱交接时身份怎么确认？", "cash_box"),
    ("交接款箱时发现封签异常怎么办？", "cash_box"),
    ("款箱保管有什么要求？", "cash_box"),
    ("款箱交接记录保存多久？", "cash_box"),
    ("款箱编码规则是什么？", "cash_box"),
    ("ATM加钞流程是什么？", "cash_box"),
    ("上门收款流程是什么？", "cash_box"),
    ("款箱交接时遇到抢劫怎么办？", "cash_box"),

    # 途中应急
    ("押运途中车辆故障怎么办？", "transit_emergency"),
    ("押运途中遇到交通事故怎么处理？", "transit_emergency"),
    ("押运途中遇到堵车怎么办？", "transit_emergency"),
    ("押运途中遇到恶劣天气怎么处理？", "transit_emergency"),
    ("押运途中遇到可疑车辆跟踪怎么办？", "transit_emergency"),
    ("押运途中车辆爆胎怎么处理？", "transit_emergency"),
    ("押运途中遇到路障怎么办？", "transit_emergency"),
    ("押运途中通讯中断怎么处理？", "transit_emergency"),
    ("押运途中有人拦车怎么办？", "transit_emergency"),
    ("押运途中遇到武装抢劫怎么办？", "transit_emergency"),
    ("押运途中发生枪击事件怎么处理？", "transit_emergency"),
    ("押运途中车辆起火怎么办？", "transit_emergency"),

    # 通讯规定
    ("押运通讯使用什么设备？", "communication"),
    ("通讯频道怎么分配？", "communication"),
    ("通讯联络的暗语规定是什么？", "communication"),
    ("通讯中断怎么处理？", "communication"),
    ("通讯记录的保存要求是什么？", "communication"),
    ("日常通讯和押运通讯有区别吗？", "communication"),
    ("对讲机使用规范是什么？", "communication"),
    ("紧急情况下的通讯流程是什么？", "communication"),
    ("通讯设备丢失怎么处理？", "communication"),
    ("通讯保密规定有哪些？", "communication"),
    ("与指挥中心的联络方式是什么？", "communication"),
    ("通讯故障的应急方案是什么？", "communication"),

    # 保险赔偿
    ("押运保险的保额是多少？", "insurance"),
    ("押运保险覆盖哪些风险？", "insurance"),
    ("发生损失怎么申请赔偿？", "insurance"),
    ("保险理赔的流程是什么？", "insurance"),
    ("保险赔偿的标准是什么？", "insurance"),
    ("哪些情况不在保险赔偿范围内？", "insurance"),
    ("保险金额度怎么确定？", "insurance"),
    ("赔偿申请需要提交哪些材料？", "insurance"),
    ("保险理赔需要多长时间？", "insurance"),
    ("押运过程中发生货物损失怎么办？", "insurance"),
    ("保险费用由谁承担？", "insurance"),
    ("超额损失怎么处理？", "insurance"),

    # ========== 制度条款相关 ==========
    # 保险金额度
    ("单次押运的保险金额上限是多少？", "insurance_amount"),
    ("保险金额度可以调整吗？", "insurance_amount"),
    ("不同类型的押运保险金额度有区别吗？", "insurance_amount"),
    ("保险金额度的审批流程是什么？", "insurance_amount"),
    ("临时增加保险金额度怎么办理？", "insurance_amount"),
    ("年度保险总额度是多少？", "insurance_amount"),
    ("保险金额度和押运标的的关系是什么？", "insurance_amount"),

    # 赔偿标准
    ("损失赔偿的计算标准是什么？", "compensation"),
    ("全额赔偿的条件是什么？", "compensation"),
    ("部分赔偿的情况有哪些？", "compensation"),
    ("赔偿金额的上限是多少？", "compensation"),
    ("因不可抗力造成的损失怎么赔偿？", "compensation"),
    ("因人为失误造成的损失怎么处理？", "compensation"),
    ("赔偿争议的解决方式是什么？", "compensation"),
    ("免赔额是多少？", "compensation"),
    ("赔偿款多久能到账？", "compensation"),
    ("第三方造成的损失由谁赔偿？", "compensation"),

    # 操作规程
    ("安保执勤的操作规程是什么？", "operation_protocol"),
    ("押运操作的关键控制点有哪些？", "operation_protocol"),
    ("安全检查的操作步骤是什么？", "operation_protocol"),
    ("应急处置的操作规程是什么？", "operation_protocol"),
    ("门卫登记的操作规范是什么？", "operation_protocol"),
    ("巡逻检查的操作标准是什么？", "operation_protocol"),
    ("枪械使用的操作规程是什么？", "operation_protocol"),
    ("车辆驾驶的操作规范是什么？", "operation_protocol"),
    ("款箱交接的操作流程是什么？", "operation_protocol"),
    ("监控室的操作规程是什么？", "operation_protocol"),
    ("消防设备操作的注意事项是什么？", "operation_protocol"),
    ("安检设备的操作标准是什么？", "operation_protocol"),

    # 合规要求
    ("安保服务需要哪些资质？", "compliance"),
    ("武装押运的合规要求有哪些？", "compliance"),
    ("安保人员需要持什么证件？", "compliance"),
    ("枪支管理的法律法规有哪些？", "compliance"),
    ("安保行业的监管要求是什么？", "compliance"),
    ("押运服务的合规标准是什么？", "compliance"),
    ("安保人员的背景审查要求是什么？", "compliance"),
    ("安保服务合同需要包含哪些条款？", "compliance"),
    ("安保人员培训有什么合规要求？", "compliance"),
    ("安保服务质量标准是什么？", "compliance"),
    ("安保行业的准入门槛是什么？", "compliance"),
    ("押运车辆需要哪些资质证件？", "compliance"),
    ("安保人员的劳动保护要求是什么？", "compliance"),
    ("违规操作的处罚措施有哪些？", "compliance"),
    ("安保服务的投诉处理流程是什么？", "compliance"),

    # ========== 口语化专业咨询 ==========
    ("这个勤务怎么弄？", "colloquial_biz"),
    ("帮我查一下押运规定", "colloquial_biz"),
    ("能不能讲讲安保制度？", "colloquial_biz"),
    ("这个制度在哪里能看到？", "colloquial_biz"),
    ("能不能帮我看看排班？", "colloquial_biz"),
    ("这个押运流程是什么来着？", "colloquial_biz"),
    ("交接班要注意啥？", "colloquial_biz"),
    ("巡逻的时候发现异常咋办？", "colloquial_biz"),
    ("枪弹管理有什么讲究？", "colloquial_biz"),
    ("押运的时候能打电话吗？", "colloquial_biz"),
    ("款箱交接有啥要注意的？", "colloquial_biz"),
    ("这个赔偿标准是多少来着？", "colloquial_biz"),
    ("安检发现东西了怎么处理？", "colloquial_biz"),
    ("排班表什么时候出？", "colloquial_biz"),
    ("对讲机没电了怎么办？", "colloquial_biz"),
    ("押运车半路坏了咋整？", "colloquial_biz"),
    ("这个勤务等级怎么调的？", "colloquial_biz"),
    ("能不能讲讲枪械保养？", "colloquial_biz"),
    ("门卫登记有什么规矩？", "colloquial_biz"),
    ("这个保险怎么赔的？", "colloquial_biz"),
]

# 安保业务领域词汇 (用于动态生成)
biz_areas = [
    "勤务等级", "门卫值守", "巡逻检查", "交接班", "突发事件处置",
    "考勤排班", "器材使用", "安检流程", "武装押运", "枪械管理",
    "车辆管理", "款箱交接", "途中应急", "通讯规定", "保险赔偿",
    "保险金额度", "赔偿标准", "操作规程", "合规要求", "应急预案",
]

biz_sub_topics = {
    "勤务等级": ["一级勤务", "二级勤务", "三级勤务", "特级勤务", "勤务升级", "勤务降级"],
    "门卫值守": ["人员登记", "车辆检查", "物品出入", "夜间值守", "访客管理", "可疑人员处置"],
    "巡逻检查": ["巡逻路线", "巡逻频次", "电子巡更", "夜间巡逻", "重点区域巡逻", "巡逻记录"],
    "交接班": ["交接流程", "交接内容", "交接记录", "装备清点", "异常情况交接"],
    "突发事件": ["火灾处置", "盗窃处置", "暴力事件", "自然灾害", "可疑物品", "群体事件"],
    "考勤排班": ["排班制度", "请假流程", "加班规定", "调休申请", "考勤异常", "节假日排班"],
    "器材使用": ["对讲机", "执法记录仪", "灭火器", "防刺服", "安检门", "金属探测器"],
    "安检流程": ["人身安检", "行李安检", "车辆安检", "违禁品处置", "安检设备维护"],
    "武装押运": ["押运准备", "押运执行", "押运交接", "押运路线", "押运保密"],
    "枪械管理": ["领枪还枪", "枪械保养", "弹药管理", "枪弹库", "持枪证", "射击训练"],
    "车辆管理": ["车辆检查", "车辆保养", "车辆保险", "GPS监控", "加油规定"],
    "款箱交接": ["交接流程", "数量核对", "封签检查", "凭证管理", "ATM加钞"],
    "途中应急": ["车辆故障", "交通事故", "恶劣天气", "可疑跟踪", "通讯中断"],
    "通讯规定": ["通讯设备", "频道分配", "暗语规定", "通讯保密", "紧急联络"],
    "保险赔偿": ["保额确定", "理赔流程", "赔偿标准", "免赔条款", "理赔材料"],
}

# ===================== 生成数据 =====================
def generate_general_knowledge():
    """生成通用知识类数据"""
    entries = []
    used_queries = set()

    # ========== 优先加入噪声反例（防止模型对特定关键词过拟合）==========
    noise_templates = [
        # 天气类反例
        "今天天气怎么样？", "明天会下雨吗？", "天气预报说明天下雨，是真的吗？",
        "最近天气变化好大啊", "今天气温多少度？", "外面冷不冷？",
        "今天适合出去运动吗？", "夏天太热了怎么办？", "冬天下雪路滑怎么开车？",
        "暴雨天出门要带什么？", "台风天怎么防护？", "雾霾天戴口罩有用吗？",
        "天气预报哪个APP比较准？", "高温天气怎么防暑降温？", "下雨天衣服怎么晾干？",
        "下雪天怎么防止摔倒？", "大雾天高速公路会封路吗？", "天气预报的降水概率是什么意思？",
        "为什么夏天下冰雹？", "龙卷风是怎么形成的？", "为什么冬天静电特别多？",
        "湿度大对身体有什么影响？", "紫外线强的时候怎么防晒？", "天气预报中的风力等级怎么分？",
        "沙尘暴天气怎么保护自己？", "今天出门需要带伞吗？", "秋天适合去哪里旅游？",
        "春天气温一般多少度？", "冬天北方一般多少度？", "南方梅雨季节是什么时候？",
        # 车辆类反例
        "私家车多久保养一次？", "车辆保险怎么买比较划算？", "车辆年检需要什么材料？",
        "车辆违章怎么查询？", "新车需要买哪些保险？", "车辆保养去4S店还是外面修车店？",
        "二手车过户需要什么手续？", "车辆GPS定位器怎么安装？", "车辆电瓶没电了怎么搭火？",
        "车辆空调不制冷怎么办？", "车辆轮胎气压多少合适？", "车辆油耗突然增高是什么原因？",
        "车辆刮擦了怎么报保险？", "车辆泡水了怎么处理？", "车辆怎么省油？",
        "电动汽车充电要多久？", "自动挡和手动挡有什么区别？", "买车要注意什么？",
        # 保险/赔偿类反例
        "医疗保险怎么报销？", "车险理赔一般要多久？", "交通事故赔偿标准是什么？",
        "买了保险出险了怎么报案？", "人寿保险和意外险有什么区别？", "医疗保险报销比例是多少？",
        "车祸对方全责怎么索赔？", "保险到期了怎么续保？", "重疾险和医疗险哪个好？",
        "交通事故误工费怎么赔偿？", "房屋保险值得买吗？", "旅游保险怎么买？",
        "社保和商保有什么区别？", "保险免赔额是什么意思？", "快递丢了怎么赔偿？",
        "养老保险交多少年？", "工伤保险怎么申请？", "失业保险金怎么领？",
        # 请假/考勤类反例
        "请假条怎么写？", "年假一般怎么安排？", "请假扣工资合法吗？",
        "病假需要什么证明？", "调休和加班互换怎么算？", "产假有多少天？",
        "婚假怎么申请？", "事假和病假哪个扣钱多？", "迟到被扣工资合理吗？",
        "加班费怎么计算？", "双休日和法定节假日加班费一样吗？", "年假没休完怎么办？",
        # 装备/器材类反例
        "对讲机频段怎么申请？", "家用灭火器怎么选择？", "手电筒什么牌子好？",
        "蓝牙耳机怎么配对？", "手机怎么连接WiFi？", "电脑开不了机怎么办？",
    ]
    for q in noise_templates:
        if q not in used_queries:
            entries.append({"query": q, "label": "通用知识"})
            used_queries.add(q)

    # ========== 动态噪声反例：用与专业咨询相同的关键词但明确是日常场景 ==========
    noise_patterns = [
        # 天气 + 日常
        lambda: f"今天{random.choice(['天气','气温','温度'])}怎么样？",
        lambda: f"明天{random.choice(['会下雨吗','天气如何','冷不冷','热不热'])}？",
        lambda: f"{random.choice(['暴雨','台风','大雪','大雾','冰雹'])}天气{random.choice(['怎么出行','要注意什么','适合出门吗','对身体的影响'])}？",
        lambda: f"{random.choice(['春天','夏天','秋天','冬天'])}的{random.choice(['天气','气温','气候'])}一般{random.choice(['多少度','怎么样','有什么特点'])}？",
        lambda: f"{random.choice(['天气预报','降水概率','风力等级','紫外线指数','空气质量'])}是什么意思？",
        lambda: f"高温天气怎么{random.choice(['防暑降温','保存食物','保养皮肤'])}？",
        lambda: f"下雨天{random.choice(['衣服怎么晾干','鞋子湿了怎么办','出行要注意什么'])}？",
        # 车辆 + 日常
        lambda: f"私家车{random.choice(['多久保养一次','保险怎么买','年检需要什么','违章怎么查','油耗太高怎么办'])}？",
        lambda: f"{random.choice(['新车','二手车','电动车'])}需要{random.choice(['买哪些保险','什么手续','注意什么'])}？",
        lambda: f"车辆{random.choice(['空调不制冷','电瓶没电','轮胎气压','刮擦了','泡水了'])}怎么办？",
        lambda: f"车辆{random.choice(['保养去4S店还是修理店','GPS怎么安装','省油技巧','过户手续'])}？",
        # 保险/赔偿 + 日常
        lambda: f"{random.choice(['医疗','车险','人寿','重疾','养老'])}保险{random.choice(['怎么报销','怎么买','哪个好','到期了怎么办'])}？",
        lambda: f"交通事故{random.choice(['赔偿标准是什么','误工费怎么算','对方全责怎么索赔'])}？",
        lambda: f"{random.choice(['快递丢了','房子漏水','手机摔坏了','旅游出事'])}怎么{random.choice(['赔偿','报保险','索赔'])}？",
        lambda: f"{random.choice(['社保','公积金','生育险','工伤险'])}怎么{random.choice(['申请','报销','领取'])}？",
        # 请假/考勤 + 日常
        lambda: f"{random.choice(['请假条','年假','病假','事假','婚假','产假'])}{random.choice(['怎么写','怎么申请','有多少天','扣工资吗'])}？",
        lambda: f"加班费{random.choice(['怎么计算','合法吗','和调休能互换吗'])}？",
        lambda: f"{random.choice(['迟到','早退','旷工'])}被{random.choice(['扣工资','辞退','处分'])}{random.choice(['合理吗','合法吗'])}？",
        # 装备/器材 + 日常
        lambda: f"家用{random.choice(['灭火器','手电筒','报警器'])}怎么{random.choice(['选择','使用','保养'])}？",
        lambda: f"{random.choice(['对讲机','蓝牙耳机','手机','电脑'])}{random.choice(['频段怎么申请','怎么配对','怎么连接WiFi','开不了机怎么办'])}？",
    ]
    noise_count = 0
    attempts = 0
    while noise_count < 200 and attempts < 2000:
        q = random.choice(noise_patterns)()
        if q not in used_queries:
            entries.append({"query": q, "label": "通用知识"})
            used_queries.add(q)
            noise_count += 1
        attempts += 1

    # 数学计算类 - 动态生成
    math_count = 0
    while math_count < 400:
        a = random.randint(1, 9999)
        b = random.randint(1, 9999)
        c = random.randint(1, 999)
        queries = [
            f"计算 {a} + {b} 等于多少？",
            f"{a} 乘以 {b} 的结果是什么？",
            f"{a} 的平方是多少？",
            f"计算 {a} - {b}",
            f"{a} 除以 {b} 的商和余数分别是多少？",
            f"求 {a} 和 {b} 的最大公约数",
            f"{a} 的 {random.randint(2,10)} 次方是多少？",
            f"计算 {a} 的平方根的近似值",
            f"斐波那契数列的第 {random.randint(5,30)} 项是多少？",
            f"{a} 的二进制表示是什么？",
            f"计算 1+2+...+{random.randint(50,500)} 的和",
            f"计算 {a}% 的 {b} 是多少",
            f"{a} 和 {b} 的最小公倍数是多少？",
            f"将十进制 {a} 转换为十六进制",
            f"{a} 加 {b} 再乘以 {c} 等于多少？",
            f"{a} 除以 {b} 等于多少？保留两位小数",
            f"{a} 的立方根是多少？",
            f"计算 {a} * {b} - {c}",
        ]
        q = random.choice(queries)
        if q not in used_queries:
            entries.append({"query": q, "label": "通用知识"})
            used_queries.add(q)
            math_count += 1

    # 通用技术问题 - 动态变体
    tech_topics = [
        ("手机", ["连接WiFi", "设置铃声", "清理缓存", "更新系统", "备份数据", "恢复出厂", "截屏", "分屏"]),
        ("电脑", ["开机慢", "运行卡", "蓝屏", "黑屏", "连不上网", "装系统", "清理垃圾", "杀毒"]),
        ("打印机", ["连接电脑", "卡纸", "墨盒更换", "驱动安装", "双面打印", "扫描文件"]),
        ("路由器", ["设置密码", "信道优化", "信号弱", "重置", "桥接", "限速"]),
        ("Excel", ["求和", "排序", "筛选", "数据透视表", "条件格式", "图表制作", "公式编写"]),
        ("Word", ["页眉页脚", "目录生成", "格式刷", "批量替换", "分栏", "水印", "修订模式"]),
    ]
    for device, ops in tech_topics:
        for op in ops:
            q_variants = [
                f"{device}怎么{op}？",
                f"{device}{op}的方法是什么？",
                f"请教一下{device}怎么{op}",
                f"{device}{op}怎么弄？",
                f"帮我看看{device}怎么{op}",
            ]
            for q in q_variants:
                if q not in used_queries:
                    entries.append({"query": q, "label": "通用知识"})
                    used_queries.add(q)

    # 概念与原理类
    concept_queries = []
    for c in concepts:
        templates_c = [
            f"什么是{c}？",
            f"解释一下{c}的概念",
            f"简述{c}的原理",
            f"请说明{c}的工作原理",
            f"什么是{c}？举个例子",
            f"解释{c}的作用",
            f"概述{c}的核心思想",
            f"为什么需要{c}？",
            f"{c}有哪些应用场景？",
            f"{c}的优缺点是什么？",
        ]
        concept_queries.extend(templates_c)

    for a, b in concept_pairs:
        templates_p = [
            f"{a}和{b}有什么区别？",
            f"{a}与{b}的不同之处在哪里？",
            f"比较一下{a}和{b}",
            f"{a}和{b}各自的优势是什么？",
            f"{a}和{b}哪个更好？",
            f"在什么场景下用{a}，什么场景下用{b}？",
        ]
        concept_queries.extend(templates_p)

    # 补充更多通用知识问题
    extra_general = [
        "什么是人工智能？",
        "什么是机器学习？",
        "什么是深度学习？",
        "什么是大数据？",
        "什么是云计算？",
        "什么是物联网？",
        "什么是区块链？",
        "什么是5G？",
        "什么是虚拟现实？",
        "什么是增强现实？",
        "什么是操作系统？",
        "什么是数据库？",
        "什么是计算机网络？",
        "什么是信息安全？",
        "什么是软件工程？",
        "什么是算法？",
        "什么是数据结构？",
        "什么是编程？",
        "什么是互联网？",
        "什么是移动互联网？",
        "什么是智能家居？",
        "什么是自动驾驶？",
        "什么是无人机？",
        "什么是3D打印？",
        "什么是新能源？",
        "什么是碳中和？",
        "什么是数字经济？",
        "什么是元宇宙？",
        "什么是ChatGPT？",
        "什么是大语言模型？",
        "什么是Prompt Engineering？",
        "什么是RAG技术？",
        "什么是Agent？",
        "什么是向量数据库？",
        "什么是Embedding？",
        "什么是Transformer？",
        "什么是BERT模型？",
        "什么是GPT模型？",
        "什么是注意力机制？",
        "什么是卷积神经网络？",
        "什么是循环神经网络？",
        "什么是生成对抗网络？",
        "什么是强化学习？",
        "什么是自然语言处理？",
        "什么是计算机视觉？",
        "什么是推荐系统？",
        "什么是知识图谱？",
        "什么是语音识别？",
        "什么是目标检测？",
        "什么是图像分割？",
        "什么是文本分类？",
        "什么是情感分析？",
        "什么是命名实体识别？",
        "什么是词向量？",
        "什么是数据仓库？",
        "什么是ETL？",
        "什么是数据湖？",
        "什么是特征工程？",
        "什么是迁移学习？",
        "什么是联邦学习？",
        "什么是知识蒸馏？",
        "什么是模型压缩？",
        "什么是量化？",
        "什么是LoRA？",
        "什么是RLHF？",
        "什么是上下文窗口？",
        "什么是Temperature？",
        "什么是Token？",
        "什么是Hallucination？",
        "什么是多模态模型？",
        "Python可以用来做什么？",
        "Java和Python哪个更适合初学者？",
        "前端开发和后端开发有什么区别？",
        "什么是全栈工程师？",
        "如何提升编程能力？",
        "学习编程最好的方式是什么？",
        "什么是开源软件？",
        "什么是API接口？",
        "什么是缓存？为什么需要缓存？",
        "什么是负载均衡？",
        "什么是容器化技术？",
        "什么是持续集成和持续部署？",
        "什么是敏捷开发？",
        "什么是设计模式？",
        "什么是RESTful架构？",
        "什么是WebSocket？",
        "什么是消息队列？",
        "什么是反向代理？",
        "什么是CDN？",
        "什么是OAuth认证？",
        "什么是JWT令牌？",
        "什么是NoSQL数据库？",
        "什么是微服务架构？",
        "什么是DevOps？",
        "什么是CI/CD？",
        "什么是CAP定理？",
        "什么是BASE理论？",
        "什么是幂等性？",
        "什么是限流？",
        "什么是熔断？",
        "什么是降级？",
        "什么是灰度发布？",
        "什么是蓝绿部署？",
        "什么是A/B测试？",
        "什么是性能优化？",
        "什么是SQL注入？如何防止？",
        "什么是XSS攻击？如何防止？",
        "什么是CSRF攻击？如何防止？",
        "什么是DDoS攻击？如何防御？",
        "什么是数据脱敏？",
        "什么是数据备份？",
        "什么是灾难恢复？",
        "什么是日志管理？",
        "什么是监控告警？",
        "什么是链路追踪？",
        "什么是配置中心？",
        "什么是服务注册与发现？",
        "什么是API网关？",
        "什么是搜索引擎？",
        "什么是推荐算法？",
        "什么是数据挖掘？",
        "什么是数据可视化？",
    ]
    concept_queries.extend(extra_general)

    for q in concept_queries:
        if q not in used_queries and len(entries) < 2500:
            entries.append({"query": q, "label": "通用知识"})
            used_queries.add(q)

    # 如果还不够，继续生成变体
    extra_patterns = [
        lambda: f"计算 {random.randint(1,9999)} + {random.randint(1,9999)} 的结果",
        lambda: f"解释{random.choice(concepts)}在实际生活中的应用",
        lambda: f"{random.choice(concepts)}适合在什么场景下使用？",
        lambda: f"学习{random.choice(concepts)}需要掌握哪些前置知识？",
        lambda: f"{random.choice(concepts)}和{random.choice(concepts)}有什么关系？",
        lambda: f"什么是{random.choice(concepts)}？用通俗的语言解释",
        lambda: f"{random.choice(concepts)}在日常生活中有哪些应用？",
        lambda: f"帮我解释一下{random.choice(concepts)}",
        lambda: f"{random.choice(concepts)}的发展历程是什么？",
        lambda: f"{random.choice(concepts)}的未来趋势是什么？",
        lambda: f"{random.randint(100,9999)}乘以{random.randint(10,999)}等于多少？",
        lambda: f"{random.randint(1,999)}和{random.randint(1,999)}的最大公约数是多少？",
        lambda: f"计算{random.randint(1,999)}的{random.randint(2,8)}次方",
    ]
    attempts = 0
    while len(entries) < 2500 and attempts < 10000:
        q = random.choice(extra_patterns)()
        if q not in used_queries:
            entries.append({"query": q, "label": "通用知识"})
            used_queries.add(q)
        attempts += 1

    random.shuffle(entries)
    return entries[:2500]


def generate_professional_consulting():
    """生成专业咨询类数据 (安保集团)"""
    entries = []
    used_queries = set()

    # 基于模板生成
    for template_str, _ in professional_templates:
        q = template_str
        if q not in used_queries:
            entries.append({"query": q, "label": "专业咨询"})
            used_queries.add(q)

    # ========== 必选样本：口语化/简短问法的专业咨询 ==========
    must_include = []
    must_include_queries = set()

    colloquial_professional = [
        "这个勤务怎么弄", "帮我查一下押运规定", "能不能讲讲安保制度",
        "这个制度在哪里看", "排班表能调吗", "交接班要注意啥",
        "巡逻发现异常咋办", "枪弹管理有什么讲究", "押运的时候能打电话吗",
        "款箱交接有啥要注意的", "赔偿标准是多少来着", "安检发现东西了怎么处理",
        "勤务等级怎么调的", "对讲机没电了怎么办", "押运车半路坏了咋整",
        "门卫登记有什么规矩", "保险怎么赔的", "这个押运流程是什么来着",
        "能不能帮我看看排班", "安保规定在哪里能找到", "有人知道枪弹管理吗",
        "枪械保养怎么做", "押运前要检查什么", "交班的时候发现少东西了怎么办",
        "巡逻打卡忘了怎么办", "请假找谁批", "加班怎么算的",
        "迟到扣多少钱", "调休怎么申请", "年假还有几天怎么查",
        "防刺服破了找谁换", "灭火器过期了怎么处理", "安检门老是报警怎么办",
        "押运路线能改吗", "枪弹库温度要求是多少", "运钞车保养周期是多久",
        "款箱封签坏了怎么办", "ATM加钞要注意什么", "上门收款流程是什么",
        "途中遇到堵车怎么办", "对讲机频道怎么切换", "暗语记不住怎么办",
        "保险额度能临时提高吗", "理赔要多久", "免赔额是多少",
        "操作规程在哪里看", "合规检查要注意什么", "资质到期了怎么续",
        "背景审查要多久", "培训合格证怎么考", "持枪证年审需要什么材料",
        "押运合同到期了怎么办", "服务质量考核标准是什么", "安保投诉怎么处理",
    ]
    for q in colloquial_professional:
        if q not in used_queries:
            must_include.append({"query": q, "label": "专业咨询"})
            used_queries.add(q)
            must_include_queries.add(q)

    # ========== 必选样本：无明确关键词的专业咨询 ==========
    no_keyword_professional = [
        "一级勤务会讲吗", "押运流程能详细说说吗", "枪械保养周期是多久",
        "款箱交接需要几个人", "途中应急方案有哪些", "通讯设备坏了找谁",
        "保险赔偿需要什么材料", "排班表什么时候出", "请假流程是什么",
        "交接班记录怎么填", "巡逻路线谁定的", "安检标准是什么",
        "门卫登记需要什么证件", "勤务等级怎么划分", "装备坏了怎么报修",
        "押运前要做什么准备", "枪弹库谁负责管理", "车辆保养在哪里做",
        "封签异常怎么处理", "加钞流程是什么", "路上遇到事故怎么办",
        "频道分配规则是什么", "理赔流程怎么走", "免赔条款有哪些",
        "操作规程最新版在哪", "合规要求有变化吗", "资质审查要多久",
        "这个赔偿怎么算的", "保额上限是多少", "临时增加保额怎么办",
        "押运任务保密要求是什么", "领枪还枪要登记吗", "弹药怎么管理",
        "巡逻打卡点怎么设置", "夜间巡逻有什么要求", "交接时装备要清点吗",
        "遇到火灾怎么处理", "发现可疑包裹怎么办", "有人闯入怎么办",
        "押运几个人一组", "押运路线能变吗", "运钞车能挪作他用吗",
        "对讲机使用有什么规范", "紧急联络方式是什么", "赔偿争议怎么解决",
    ]
    for q in no_keyword_professional:
        if q not in used_queries:
            must_include.append({"query": q, "label": "专业咨询"})
            used_queries.add(q)
            must_include_queries.add(q)

    # ========== 动态生成更多专业咨询样本 ==========
    extra_professional = []

    # 基于 biz_sub_topics 动态生成 — 区分流程类和事件类模板
    # 事件/应急类 topic（不适用"操作流程"、"常见错误"等模板）
    event_topics = {
        "突发事件", "途中应急",
    }

    for area, topics in biz_sub_topics.items():
        for topic in topics:
            if area in event_topics:
                # 事件类：使用应急处置相关模板
                extras = [
                    f"安保执勤中{topic}的应急处置流程是什么？",
                    f"{area}时遇到{topic}怎么处理？",
                    f"{topic}的应急预案是什么？",
                    f"押运途中发生{topic}应该怎么办？",
                    f"{topic}的处置注意事项有哪些？",
                    f"{area}中{topic}情况下的安全要求是什么？",
                    f"遇到{topic}时安保人员应该怎么做？",
                    f"{topic}发生后的信息报告流程是什么？",
                    f"{area}关于{topic}的防范措施有哪些？",
                    f"{topic}处置完毕后需要做什么？",
                ]
            else:
                # 流程/制度类：使用制度规范相关模板，始终带安保上下文
                extras = [
                    f"安保{area}中关于{topic}的规定是什么？",
                    f"{area}制度下{topic}的操作流程是怎样的？",
                    f"{area}中{topic}需要注意哪些事项？",
                    f"请介绍一下安保{topic}的相关制度",
                    f"{area}中{topic}的执行标准是什么？",
                    f"{topic}和{area}其他环节有什么关系？",
                    f"关于安保{topic}有哪些具体要求？",
                    f"{area}中{topic}出了问题怎么处理？",
                    f"{area}培训中{topic}的内容包括哪些？",
                    f"{area}考核中{topic}的标准是什么？",
                    f"能不能讲讲安保{topic}的规定？",
                    f"{area}的{topic}具体怎么操作？",
                    f"帮我查一下{area}中{topic}的规定",
                    f"{area}中{topic}的正确做法是什么？",
                    f"新人入职需要了解{area}的{topic}吗？",
                ]
            extra_professional.extend(extras)

    # 基于 biz_areas 动态组合生成（始终带安保上下文）
    for area in biz_areas:
        extras = [
            f"安保{area}的基本内容是什么？",
            f"{area}制度在哪里可以查看？",
            f"关于安保{area}有哪些规定？",
            f"{area}的具体要求是什么？",
            f"想了解安保{area}的相关内容",
            f"{area}制度最近有什么变化？",
            f"{area}培训什么时候开始？",
            f"{area}的检查标准是什么？",
            f"新人入职需要了解{area}的哪些内容？",
            f"{area}中有哪些常见问题？",
            f"安保{area}出了差错怎么处理？",
            f"{area}的责任人是谁？",
            f"能不能详细讲讲{area}制度？",
            f"帮我看看{area}的管理规定",
            f"{area}制度和以前有什么变化？",
        ]
        extra_professional.extend(extras)

    # 跨领域组合问题
    cross_area_questions = [
        "押运途中车辆故障需要启动什么等级的勤务？",
        "门卫值守时发现可疑物品需要按什么流程处理？",
        "巡逻中发现火灾隐患需要通知哪些部门？",
        "交接班时接到押运任务怎么处理？",
        "安检过程中发现枪支怎么处理？",
        "押运前车辆检查不合格怎么办？",
        "枪械保养记录和押运任务有关系吗？",
        "排班表和勤务等级怎么对应？",
        "考勤异常会影响勤务等级评定吗？",
        "押运保险和车辆保险有重叠吗？",
        "款箱交接和押运交接是同一个流程吗？",
        "通讯中断时押运和门卫分别怎么处理？",
        "突发事件处置后需要写什么报告？",
        "器材损坏报修和装备清点有什么关系？",
        "合规检查中押运和执勤分别查什么？",
        "赔偿标准和保险金额度是什么关系？",
        "操作规程中押运和门卫有什么区别？",
        "途中应急和突发事件处置有什么区别？",
        "押运保密规定和通讯保密规定有什么联系？",
        "门卫值守和安检流程有什么衔接？",
    ]
    extra_professional.extend(cross_area_questions)

    # 场景化问题
    scenario_questions = [
        "银行网点押运款箱到达后，门卫应该做什么？",
        "大型活动期间勤务等级如何调整？",
        "暴雨天气巡逻路线需要怎么调整？",
        "春节期间排班有什么特殊安排？",
        "新客户首次押运需要注意什么？",
        "押运途中遇到道路施工怎么绕行？",
        "新员工第一次独立门卫值守要注意什么？",
        "枪弹库搬迁需要走什么流程？",
        "运钞车更换新车辆需要办什么手续？",
        "ATM机加钞时发现钞箱异常怎么处理？",
        "上门收款时客户单位临时变更地点怎么办？",
        "重大节日安保方案怎么制定？",
        "年度押运保险续保流程是什么？",
        "安保人员退休时枪械和证件怎么处理？",
        "新入职安保人员需要参加哪些培训？",
        "季度安保演练计划怎么制定？",
        "押运路线经过学校区域需要注意什么？",
        "夜间金库值守有什么特殊要求？",
        "高温天气押运有什么注意事项？",
        "押运车辆年检到期怎么处理？",
    ]
    extra_professional.extend(scenario_questions)

    for q in extra_professional:
        if q not in used_queries:
            entries.append({"query": q, "label": "专业咨询"})
            used_queries.add(q)

    # 如果还不够，继续生成变体（始终带安保上下文）
    extra_patterns_p = [
        lambda: f"安保{random.choice(biz_areas)}的具体内容是什么？",
        lambda: f"想了解安保{random.choice(biz_areas)}的相关规定",
        lambda: f"安保{random.choice(biz_areas)}{random.choice(['值不值得注意', '有什么变化', '难不难', '需要培训吗', '有新规定吗'])}？",
        lambda: f"请问安保{random.choice(biz_areas)}{random.choice(['需要什么条件', '要多久', '流程是什么', '在哪里办理', '有变化吗'])}？",
        lambda: f"安保{random.choice(biz_areas)}的{random.choice(['操作流程', '管理制度', '考核标准', '培训要求', '注意事项'])}是什么？",
        lambda: f"安保{random.choice(biz_areas)}出了{random.choice(['问题', '差错', '事故', '异常', '故障'])}怎么处理？",
        lambda: f"关于安保{random.choice(biz_areas)}，{random.choice(['新人需要了解什么', '老员工需要复习什么', '领导关注什么', '检查重点是什么'])}？",
        lambda: f"安保{random.choice(biz_areas)}的{random.choice(['最新规定', '历史变化', '行业标准', '法律依据', '执行细节'])}是什么？",
    ]
    attempts = 0
    while len(entries) < 2500 and attempts < 10000:
        q = random.choice(extra_patterns_p)()
        if q not in used_queries:
            entries.append({"query": q, "label": "专业咨询"})
            used_queries.add(q)
        attempts += 1

    # 打乱模板/额外样本，截取剩余名额，再与必选样本合并
    random.shuffle(entries)
    remaining_slots = 2500 - len(must_include)
    result = entries[:remaining_slots] + must_include
    random.shuffle(result)
    return result


def main():
    print("开始生成安保集团查询分类训练数据...")

    # 生成两个类别的数据
    general_entries = generate_general_knowledge()
    professional_entries = generate_professional_consulting()

    print(f"通用知识: {len(general_entries)} 条")
    print(f"专业咨询: {len(professional_entries)} 条")

    # 合并并打乱
    all_entries = general_entries + professional_entries
    random.shuffle(all_entries)

    print(f"总计: {len(all_entries)} 条")

    # 写入文件
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_generic_5000.json")
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"数据已保存到 {output_path}")

    # 验证
    with open(output_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    general_count = sum(1 for line in lines if '"通用知识"' in line)
    professional_count = sum(1 for line in lines if '"专业咨询"' in line)
    print(f"\n验证结果:")
    print(f"总行数: {len(lines)}")
    print(f"通用知识: {general_count} 条")
    print(f"专业咨询: {professional_count} 条")
    print(f"比例: {general_count}:{professional_count}")


if __name__ == "__main__":
    main()
