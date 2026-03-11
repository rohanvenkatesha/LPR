create database license;

use license;


-- Create the main table to store every detection
CREATE TABLE license_master (
id INT IDENTITY(1,1) PRIMARY KEY,
licensenumber NVARCHAR(20) NOT NULL,
placename NVARCHAR(100),
timeslot DATETIME DEFAULT GETDATE(),
filepath VARBINARY(MAX), -- Stores the cropped plate image
datedifference INT DEFAULT 0
);

-- Create a summary table to count visits per car
CREATE TABLE license_count (
licensenumber NVARCHAR(20) PRIMARY KEY,
placename NVARCHAR(100),
totalcount INT DEFAULT 1,
timeslot DATETIME DEFAULT GETDATE(),
filepath VARBINARY(MAX)
);

select * from license_master;
select * from license_count;