import multiprocessing

from fff01x_v16t100_opms_beta import *

if __name__ == '__main__':
    symbol_placeholder = "USDZAR"
    symbol_list_operate = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    log = C1Help(symbol_placeholder).d0log
    title = C1Help(symbol_placeholder).d0title


    class C0Main:
        @staticmethod
        def d0program_start():
            """ 整个程序的启动入口
            """
            log(title("启动程序", position="up"))
            log("名称: <FreeFlyFrame> by JesseLiu, NO.fff01x_v16t100_opms_beta.py")
            log(f"标的: 占位={symbol_placeholder}, 操作={symbol_list_operate}")
            log(title("启动程序", position="down"))

        @staticmethod
        def d0process_start():
            """ 根据操作标的分配进程
            """
            log(title("启动进程", position="up"))
            list_process = []
            for i in symbol_list_operate:
                process = multiprocessing.Process(target=C0Core(i).d0ploy_start)
                process.start()
                list_process.append(process)
                time.sleep(1)
            log(title("启动进程", position="down"))
            for i in list_process:
                i.join()

        @staticmethod
        def d0program_quit():
            """ 整个程序的退出口
            """
            log(title("退出程序", position="up"))
            MetaTrader5.shutdown()
            log(title("退出程序", position="down"))


    C0Main.d0program_start()
    C0Core(symbol_placeholder).d0common_start()
    C0Main.d0process_start()
    C0Core(symbol_placeholder).d0common_quit()
    C0Main.d0program_quit()
