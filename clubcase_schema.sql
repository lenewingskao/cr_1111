CREATE TABLE `duty1111` (
  `did` varchar(6) NOT NULL,
  `dname` varchar(20) DEFAULT NULL,
  `level` smallint(6) DEFAULT '1',
  PRIMARY KEY (`did`),
  KEY `DUTY11_A` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `joblist1111` (
  `did` varchar(6) DEFAULT NULL,
  `title` varchar(300) DEFAULT NULL,
  `jburl` varchar(300) DEFAULT NULL,
  `corp` varchar(300) DEFAULT NULL,
  `courl` varchar(300) DEFAULT NULL,
  `crdate` datetime DEFAULT NULL,
  KEY `A` (`jburl`),
  KEY `B` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci