CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  customer_name VARCHAR(64) NOT NULL,
  city VARCHAR(32) NOT NULL,
  customer_level VARCHAR(32) NOT NULL,
  registered_at DATE NOT NULL
);

CREATE TABLE products (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL,
  list_price DECIMAL(10,2) NOT NULL,
  unit_cost DECIMAL(10,2) NOT NULL,
  is_active TINYINT NOT NULL
);

CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_date DATE NOT NULL,
  status VARCHAR(32) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  item_id INT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  line_amount DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
  payment_id INT PRIMARY KEY,
  order_id INT NOT NULL,
  payment_method VARCHAR(32) NOT NULL,
  paid_amount DECIMAL(10,2) NOT NULL,
  payment_status VARCHAR(32) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE refunds (
  refund_id INT PRIMARY KEY,
  item_id INT NOT NULL,
  refund_amount DECIMAL(10,2) NOT NULL,
  refund_reason VARCHAR(128) NOT NULL,
  refund_status VARCHAR(32) NOT NULL,
  FOREIGN KEY (item_id) REFERENCES order_items(item_id)
);

CREATE TABLE marketing_events (
  event_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  event_name VARCHAR(128) NOT NULL,
  channel VARCHAR(64) NOT NULL,
  event_date DATE NOT NULL,
  converted TINYINT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE customer_feedback (
  feedback_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_id INT NOT NULL,
  rating INT NOT NULL,
  feedback_text VARCHAR(512) NOT NULL,
  created_at DATE NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO customers VALUES
  (1,'Alice','北京','gold','2026-01-04'),
  (2,'Bob','上海','silver','2026-02-11'),
  (3,'Cathy','深圳','gold','2026-03-02'),
  (4,'David','杭州','bronze','2026-03-18'),
  (5,'Eva','北京','platinum','2026-04-01'),
  (6,'Frank','成都','silver','2026-04-18'),
  (7,'Grace','武汉','bronze','2026-05-01'),
  (8,'Henry','广州','gold','2026-05-15');

INSERT INTO products VALUES
  (1,'智能音箱','硬件',299.00,120.00,1),
  (2,'AI写作会员','订阅',99.00,15.00,1),
  (3,'数据分析课','课程',499.00,80.00,1),
  (4,'智能手环','硬件',199.00,70.00,1),
  (5,'企业插件包','软件',899.00,200.00,1),
  (6,'降噪耳机','硬件',599.00,240.00,1);

INSERT INTO orders VALUES
  (1001,1,DATE_SUB(CURDATE(), INTERVAL 5 DAY),'paid',398.00),
  (1002,2,DATE_SUB(CURDATE(), INTERVAL 12 DAY),'paid',998.00),
  (1003,3,DATE_SUB(CURDATE(), INTERVAL 25 DAY),'refunded',599.00),
  (1004,4,DATE_SUB(CURDATE(), INTERVAL 75 DAY),'paid',199.00),
  (1005,5,DATE_SUB(CURDATE(), INTERVAL 2 DAY),'paid',1397.00),
  (1006,1,DATE_SUB(CURDATE(), INTERVAL 35 DAY),'paid',99.00),
  (1007,6,DATE_SUB(CURDATE(), INTERVAL 18 DAY),'paid',499.00),
  (1008,8,DATE_SUB(CURDATE(), INTERVAL 8 DAY),'paid',798.00);

INSERT INTO order_items VALUES
  (1,1001,1,1,299.00,299.00),
  (2,1001,2,1,99.00,99.00),
  (3,1002,3,2,499.00,998.00),
  (4,1003,6,1,599.00,599.00),
  (5,1004,4,1,199.00,199.00),
  (6,1005,5,1,899.00,899.00),
  (7,1005,3,1,499.00,499.00),
  (8,1006,2,1,99.00,99.00),
  (9,1007,3,1,499.00,499.00),
  (10,1008,1,1,299.00,299.00),
  (11,1008,4,1,199.00,199.00),
  (12,1008,2,3,100.00,300.00);

INSERT INTO payments VALUES
  (1,1001,'alipay',398.00,'success'),
  (2,1002,'card',998.00,'success'),
  (3,1003,'wechat',599.00,'success'),
  (4,1004,'alipay',199.00,'success'),
  (5,1005,'card',1397.00,'success'),
  (6,1006,'wechat',99.00,'success'),
  (7,1007,'alipay',499.00,'success'),
  (8,1008,'card',798.00,'success');

INSERT INTO refunds VALUES
  (1,4,599.00,'降噪效果不满意','approved'),
  (2,3,200.00,'课程重复购买','approved'),
  (3,11,199.00,'尺寸不合适','approved');

INSERT INTO marketing_events VALUES
  (1,1,'618促销','短信',DATE_SUB(CURDATE(), INTERVAL 20 DAY),1),
  (2,2,'新品试用','公众号',DATE_SUB(CURDATE(), INTERVAL 70 DAY),0),
  (3,4,'老客召回','邮件',DATE_SUB(CURDATE(), INTERVAL 10 DAY),0),
  (4,7,'618促销','短信',DATE_SUB(CURDATE(), INTERVAL 15 DAY),0),
  (5,8,'会员日','App Push',DATE_SUB(CURDATE(), INTERVAL 9 DAY),1);

INSERT INTO customer_feedback VALUES
  (1,3,1003,2,'耳机降噪没有预期好',DATE_SUB(CURDATE(), INTERVAL 24 DAY)),
  (2,5,1005,5,'企业插件很实用',DATE_SUB(CURDATE(), INTERVAL 1 DAY)),
  (3,2,1002,3,'课程内容还可以',DATE_SUB(CURDATE(), INTERVAL 10 DAY)),
  (4,8,1008,2,'物流慢且包装破损',DATE_SUB(CURDATE(), INTERVAL 6 DAY)),
  (5,1,1001,5,'音箱体验很好',DATE_SUB(CURDATE(), INTERVAL 4 DAY));
