using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;

namespace ConsoleTemplate.Objects
{
    // Možnost efektivně se připojovat k DB
    public static class DbConfig
    {
        /// <summary>
        /// Vrací ConnectionString pro SQL Server.
        /// </summary>
        public static string ConnectionString =>
            new SqlConnectionStringBuilder
            {
                DataSource = @"localhost\SQLEXPRESS",
                InitialCatalog = "ContactManager",
                IntegratedSecurity = true,
                TrustServerCertificate = true
            }.ConnectionString;

        // poté lze aplikovat takto
        // using var conn = new SqlConnection(DbConfig.ConnectionString);
        // conn.Open();
    }

    public class User
    {
        /// <summary>Jedinečný identifikátor uživatele.</summary>
        public int ID { get; set; }
        /// <summary>Přihlašovací jméno uživatele.</summary>
        public string Username { get; set; } = null!;
        /// <summary>Hash hesla uživatele (SHA-256, Base64).</summary>
        public string PasswordHash { get; set; } = null!;

        /// <inheritdoc/>
        public User()
        {
        }
    }

}
