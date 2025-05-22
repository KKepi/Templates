using Microsoft.Data.SqlClient;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DesktopTemplate.Objects
{
    public class User
    {
        public int ID { get; set; }
        public string Username { get; set; } = null!;
        public string Jmeno { get; set; } = null!;
        public string Prijmeni { get; set; } = null!;
        public string Role { get; set; } = null!;
        public string PasswordHash { get; set; } = null!;
    }

    // ostatní dle tabulek v Models.cs

    // pomocník pro připojování k databázi
    public static class DbConfig
    {
        /// <summary>
        /// Vrací ConnectionString pro SQL Server.
        /// </summary>
        public static string ConnectionString =>
            new SqlConnectionStringBuilder
            {
                DataSource = @"localhost\SQLEXPRESS",
                InitialCatalog = "JmenoDatabaze", // <- změnit!
                IntegratedSecurity = true,
                TrustServerCertificate = true
            }.ConnectionString;

        // using var conn = new SqlConnection(DbConfig.ConnectionString);
        // conn.Open();
    }


}
