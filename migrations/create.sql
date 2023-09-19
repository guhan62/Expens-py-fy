-- Create DB
-- Split
CREATE TABLE IF NOT EXISTS SPLIT_LABEL(
    Id INTEGER PRIMARY KEY,
    Description  VARCHAR(60)
);
INSERT OR IGNORE INTO SPLIT_LABEL(Id, Description) VALUES (1, 'PERSONAL'), (2, 'ALREADY_SPLIT'),(3, 'TO_SPLIT'), (4, 'TBD'), (5, 'PARTIAL_SPLIT');

CREATE TABLE IF NOT EXISTS PAY_LABEL(
    Id INTEGER PRIMARY KEY,
    Description  VARCHAR(60)
);
INSERT OR IGNORE INTO PAY_LABEL(Id, Description) VALUES (1, 'BANK'), (2, 'BOFA'), (3, 'AMEX'), (4, 'DISCOVER'), (5, 'CITI'), (6, 'CASH');


-- id,HASH,Date,Description,Amount,Comments,Split_Id
CREATE TABLE IF NOT EXISTS EXPENSES(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    HASH  text,
    Date text,
    Description text,
    -- Actual Bill
    Original_Amount REAL Default(NULL),
    -- Amount to be Shared
    Amount REAL,
    Pay_Id INTEGER,
    Category text,
    Split_Id INTEGER Default(1),
    Comments text,
    Splitwise_Label INTEGER Default(18),
    Splitwise_Id INTEGER Default(NULL),
    FOREIGN KEY(Pay_Id) REFERENCES PAY_LABEL(Id),
    FOREIGN KEY(Split_Id) REFERENCES SPLIT_LABEL(Id)
);
