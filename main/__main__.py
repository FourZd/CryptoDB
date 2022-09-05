from eth import eth_main, bsc_main
import multiprocessing
class CombinedChains():

    def start_bsc(self):
        bsc_main.start_work()
    
    def start_eth(self):
        eth_main.start_work()

    
    def infinity_loop(self):
        bsc_proc = multiprocessing.Process(target=self.start_bsc)
        eth_proc = multiprocessing.Process(target=self.start_eth)
        bsc_proc.start()
        eth_proc.start()

combined = CombinedChains()
if __name__ == '__main__':
    combined.infinity_loop()
