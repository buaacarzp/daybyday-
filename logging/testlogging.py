import logging
logging.basicConfig(format="%(asctime)s,%(levelname)s,%(filename)s:%(lineno)s,%(message)s",filename='demo.log',filemode='w',level=logging.DEBUG)
logging.debug("nothing")
age = 18
name ="zhoupeng"
logging.debug(f"age={age},name={name}")