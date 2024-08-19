CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) NOT NULL
);

CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    CategoryName NVARCHAR(100) NOT NULL
);

CREATE TABLE Projects (
    ProjectID INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(200) NOT NULL,
    CategoryID INT NOT NULL,
    UserID INT,
    CONSTRAINT FK_Projects_Categories FOREIGN KEY (CategoryID)
        REFERENCES Categories(CategoryID),
    CONSTRAINT FK_Projects_Users FOREIGN KEY (UserID)
        REFERENCES Users(UserID)
);


SELECT p.ProjectID, p.Title, c.CategoryName, u.Username 
        FROM Projects p
        JOIN Categories c ON p.CategoryID = c.CategoryID
        JOIN Users u ON p.UserID = u.UserID
