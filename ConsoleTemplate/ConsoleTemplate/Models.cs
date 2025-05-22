using System;
using System.Text;
using Microsoft.Data.SqlClient;
using ConsoleTemplate.Objects;

namespace ConsoleTemplate.Models
{
    class Database
    {
        public SqlConnection myConn;

        public Database()
        {
            //                         změnit!
            EnsureDatabaseExists("JmenoDb");
            //                                                                               změnit!
            string connectionString = "Data Source=localhost\\SQLEXPRESS;Initial Catalog=ContactManager;Integrated Security=True;TrustServerCertificate=True;";

            myConn = new SqlConnection(connectionString);


            try
            {
                myConn.Open();

                // základní tabulka pro vytvoření uživatelů
                CreateTableIfNotExists("Users", @"
                    CREATE TABLE Users (
                        ID INT IDENTITY(1,1) PRIMARY KEY,
                        Username NVARCHAR(50) NOT NULL UNIQUE,
                        PasswordHash NVARCHAR(256) NOT NULL
                    )
                ");

                // doplnit potřebné tabulky

                InsertDefaultAdmin();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Chyba při inicializaci databáze: " + ex.Message);
            }
            finally
            {
                myConn.Close();
            }
        }

        public void CreateTableIfNotExists(string tableName, string createSql)
        {
            string checkQuery = $@"
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{tableName}')
                BEGIN
                    {createSql}
                END";

            using (SqlCommand command = new SqlCommand(checkQuery, myConn))
            {
                command.ExecuteNonQuery();
            }
        }

        private void EnsureDatabaseExists(string dbName)
        {
            string masterConnection = "Data Source=localhost\\SQLEXPRESS;Initial Catalog=master;Integrated Security=True;TrustServerCertificate=True;";

            using (var conn = new SqlConnection(masterConnection))
            {
                conn.Open();

                var cmd = new SqlCommand($@"
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{dbName}')
            BEGIN
                CREATE DATABASE [{dbName}]
            END
        ", conn);

                cmd.ExecuteNonQuery();
            }
        }

        private void InsertDefaultAdmin()
        {
            string username = "admin";
            string passwordHash = HashPassword("admin");

            string checkQuery = "SELECT COUNT(*) FROM Users WHERE Username = @username";

            using (SqlCommand checkCmd = new SqlCommand(checkQuery, myConn))
            {
                checkCmd.Parameters.AddWithValue("@username", username);
                int count = (int)checkCmd.ExecuteScalar();

                if (count == 0)
                {
                    string insertQuery = "INSERT INTO Users (Username, PasswordHash) VALUES (@username, @passwordHash)";

                    using (SqlCommand insertCmd = new SqlCommand(insertQuery, myConn))
                    {
                        insertCmd.Parameters.AddWithValue("@username", username);
                        insertCmd.Parameters.AddWithValue("@passwordHash", passwordHash);

                        insertCmd.ExecuteNonQuery();
                    }
                }
            }
        }

        public static string HashPassword(string password)
        {
            using (var sha = System.Security.Cryptography.SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(password);
                byte[] hash = sha.ComputeHash(bytes);
                return Convert.ToBase64String(hash);
            }
        }
    }
}
