using Microsoft.Data.SqlClient;
using Microsoft.IdentityModel.Protocols.Configuration;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using static Azure.Core.HttpHeader;

namespace ContactManager.Objects
{
    /// <summary>
    /// Statická třída poskytující připojovací řetězec k databázi.
    /// </summary>
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
    }

    /// <summary>
    /// Rozhraní umožňující klonování objektů (vzor Prototype).
    /// </summary>
    /// <typeparam name="T">Typ objektu, který lze klonovat.</typeparam>
    public interface IPrototype<T>
    {
        /// <summary>
        /// Vytvoří povrchovou kopii aktuální instance.
        /// </summary>
        /// <returns>Kopie objektu typu T.</returns>
        T Clone();
    }

    /// <summary>
    /// Reprezentuje uživatele aplikace s přihlašovacími údaji.
    /// </summary>
    public class User : IPrototype<User>
    {
        /// <summary>Jedinečný identifikátor uživatele.</summary>
        public int ID { get; set; }
        /// <summary>Přihlašovací jméno uživatele.</summary>
        public string Username { get; set; } = null!;
        /// <summary>Hash hesla uživatele (SHA-256, Base64).</summary>
        public string PasswordHash { get; set; } = null!;

        /// <inheritdoc/>
        public User Clone()
        {
            return (User)this.MemberwiseClone();
        }
    }

    /// <summary>
    /// Reprezentuje kontakt spojený s uživatelem.
    /// </summary>
    public class Contact
    {
        /// <summary>Jedinečný identifikátor kontaktu.</summary>
        public int ID { get; set; }
        /// <summary>Název (jméno) kontaktu.</summary>
        public string Nazev { get; set; } = null!;
        /// <summary>ID uživatele, ke kterému kontakt náleží.</summary>
        public int UserID { get; set; }
    }

    /// <summary>
    /// Rozhraní pro příkazový vzor definující metody Execute a Undo.
    /// </summary>
    public interface ICommander
    {
        /// <summary>Provede příkazovou akci.</summary>
        void Execute();
        /// <summary>Zruší dříve provedenou akci.</summary>
        void Undo();
    }

    /// <summary>
    /// Příkaz pro kopírování kontaktu (vzor Command).
    /// </summary>
    public class CopyContact : ICommander
    {
        private readonly User _user;
        private readonly Contact _contact;
        /// <summary>Poslední vložený (zkopírovaný) kontakt pro Undo.</summary>
        public Contact lastAddedContact;

        /// <summary>
        /// Inicializuje nový příkaz CopyContact.
        /// </summary>
        /// <param name="user">Uživatel, který kopii provádí.</param>
        /// <param name="contact">Kontakt, který se kopíruje.</param>
        public CopyContact(User user, Contact contact)
        {
            _user = user;
            _contact = contact;
            lastAddedContact = null;
        }

        /// <inheritdoc/>
        public void Execute()
        {
            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();

            const string sql = @"
                SELECT c.Nazev
                FROM Contacts c
                WHERE c.Nazev = @nazev";

            using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@nazev", _contact.Nazev);

            using (var reader = cmd.ExecuteReader())
            {
                while (reader.Read())
                {
                    var contact = new Contact
                    {
                        Nazev = reader.GetString(0),
                        UserID = _user.ID
                    };
                    Console.WriteLine($"Contact found: {contact.Nazev}");
                }
            }

            const string sql2 = @"
                INSERT INTO Contacts (Nazev, UserID)
                OUTPUT INSERTED.ID
                VALUES (@nazev, @uid)";

            using var insertCmd = new SqlCommand(sql2, conn);
            insertCmd.Parameters.AddWithValue("@nazev", _contact.Nazev);
            insertCmd.Parameters.AddWithValue("@uid", _user.ID);

            var newId = (int)insertCmd.ExecuteScalar();
            var newContact = new Contact
            {
                ID = newId,
                Nazev = _contact.Nazev,
                UserID = _user.ID
            };
            lastAddedContact = newContact;
        }

        /// <inheritdoc/>
        public void Undo()
        {
            if (lastAddedContact != null)
            {
                using var conn = new SqlConnection(DbConfig.ConnectionString);
                conn.Open();
                const string sql = @"
                    DELETE FROM Contacts
                    WHERE Nazev = @nazev";
                using var cmd = new SqlCommand(sql, conn);
                cmd.Parameters.AddWithValue("@nazev", lastAddedContact.Nazev);
                cmd.ExecuteNonQuery();
            }
            else
            {
                Console.WriteLine("No contact to undo.");
            }
        }
    }

    /// <summary>
    /// Příkaz pro smazání existujícího kontaktu.
    /// </summary>
    public class DeleteContact : ICommander
    {
        private readonly User _user;
        private readonly Contact _contact;
        /// <summary>
        /// Inicializuje nový příkaz DeleteContact.
        /// </summary>
        public DeleteContact(User user, Contact contact)
        {
            _user = user;
            _contact = contact;
        }
        /// <inheritdoc/>
        public void Execute()
        {
            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();

            const string sql = @"
                    DELETE FROM Contacts
                    WHERE Nazev = @nazev";
            using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@nazev", _contact.Nazev);
            cmd.ExecuteNonQuery();

        }

        /// <inheritdoc/>
        public void Undo()
        {
            // Implement the logic to undo the delete
            Console.WriteLine($"Undoing delete of contact '{_contact.Nazev}' for user '{_user.Username}'");
        }
    }

    /// <summary>
    /// Příkaz pro přidání nového kontaktu.
    /// </summary>
    public class AddContact : ICommander
    {
        private readonly User _user;
        private readonly Contact _contact;
        /// <summary>Poslední vložený kontakt pro Undo.</summary>
        public Contact lastAddedContact;
        /// <summary>
        /// Inicializuje nový příkaz AddContact.
        /// </summary>
        /// <param name="user">Uživatel, který kontakt přidává.</param>
        /// <param name="contact">Kontakt k přidání.</param>
        public AddContact(User user, Contact contact)
        {
            _user = user;
            _contact = contact;
            lastAddedContact = null;
        }
        /// <inheritdoc/>
        public void Execute()
        {
            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();

            const string sql = @"
                INSERT INTO Contacts (Nazev, UserID)
                OUTPUT INSERTED.ID
                VALUES (@nazev, @uid)";

            using var insertCmd = new SqlCommand(sql, conn);
            insertCmd.Parameters.AddWithValue("@nazev", _contact.Nazev);
            insertCmd.Parameters.AddWithValue("@uid", _user.ID);

            var newId = (int)insertCmd.ExecuteScalar();
            var newContact = new Contact
            {
                ID = newId,
                Nazev = _contact.Nazev,
                UserID = _user.ID
            };

            lastAddedContact = newContact;
        }
        /// <inheritdoc/>
        public void Undo()
        {
            if (lastAddedContact != null)
            {
                using var conn = new SqlConnection(DbConfig.ConnectionString);

                conn.Open();
                const string sql = @"
                    DELETE FROM Contacts
                    WHERE Nazev = @nazev";
                using var cmd = new SqlCommand(sql, conn);
                cmd.Parameters.AddWithValue("@nazev", lastAddedContact.Nazev);
                cmd.ExecuteNonQuery();
            }
            else
            {
                Console.WriteLine("No contact to undo.");
            }
        }
    }

    /// <summary>
    /// Správce provádění příkazů s podporou Undo/Redo.
    /// </summary>
    public class Controller
    {
        private readonly Stack<ICommander> _undoStack = new();
        private readonly Stack<ICommander> _redoStack = new();

        public Controller()
        {
        }

        /// <summary>Provede příkaz a uloží ho do historie pro Undo/Redo.</summary>
        public void ExecuteCommand(ICommander command)
        {
            command.Execute();
            _undoStack.Push(command);
            _redoStack.Clear();
        }

        /// <summary>Vrátí zpět poslední provedený příkaz.</summary>
        public void Undo()
        {
            if (_undoStack.Count == 0) return;
            var cmd = _undoStack.Pop();
            cmd.Undo();
            _redoStack.Push(cmd);
        }

        /// <summary>Opakuje poslední vrácený příkaz.</summary>
        public void Redo()
        {
            if (_redoStack.Count == 0) return;
            var cmd = _redoStack.Pop();
            cmd.Execute();
            _undoStack.Push(cmd);
        }
    }

    /// <summary>
    /// Umožňuje procházet kontakty uživatele pomocí foreach (Iterator Pattern).
    /// </summary>
    public class UserContacts : IEnumerable<Contact>
    {
        private readonly User _user;

        /// <summary>Inicializuje nové procházení kontaktů pro uživatele.</summary>
        public UserContacts(User user)
        {
            _user = user;
        }

        /// <summary>Načte kontakty z databáze do seznamu.</summary>
        /// <returns>Seznam kontaktů uživatele.</returns>
        public List<Contact> loadContacts()
        {
            // Load contacts from the database or any other source
            Console.WriteLine($"Loading contacts for user '{_user.Username}'");

            var contacts = new List<Contact>();

            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();

            const string sql = @"
            SELECT c.ID, c.Nazev
            FROM Users u
            JOIN Contacts c ON u.ID = c.UserID
            WHERE u.ID = @uid";

            using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@uid", _user.ID);

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                var contact = new Contact
                {
                    ID = reader.GetInt32(0),
                    Nazev = reader.GetString(1),
                    UserID = _user.ID
                };
                contacts.Add(contact);
            }

            return contacts;
        }

        /// <inheritdoc/>
        public IEnumerator<Contact> GetEnumerator()
        {
            foreach (var c in loadContacts())
                yield return c;
        }

        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator()
        => GetEnumerator();
    }

    /// <summary>
    /// Zajišťuje registraci a přihlášení uživatelů.
    /// </summary>
    public class CredentialProvider
    {
        public CredentialProvider()
        { }

        public User Register(string username, string password)
        {
            /// <summary>Registruje nového uživatele.</summary>
            /// <param name="username">Uživatelské jméno.</param>
            /// <param name="password">Heslo v čistém textu.</summary>
            /// <returns>Vytvořený <see cref="User"/> s ID a hash hesla.</returns>
            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();

            // Check if the username already exists
            const string checkSql = "SELECT COUNT(*) FROM Users WHERE Username = @username";
            using var checkCmd = new SqlCommand(checkSql, conn);
            checkCmd.Parameters.AddWithValue("@username", username);
            int count = (int)checkCmd.ExecuteScalar();
            if (count > 0)
            {
                throw new Exception("Username already exists.");
            }

            const string sql = @"
                INSERT INTO Users (Username, PasswordHash)
                OUTPUT INSERTED.ID
                VALUES (@username, @password)";

            using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@username", username);
            cmd.Parameters.AddWithValue("@password", HashPassword(password));
            var newId = (int)cmd.ExecuteScalar();
            return new User
            {
                ID = newId,
                Username = username,
                PasswordHash = HashPassword(password)
            };
        }

        /// <summary>Přihlásí existujícího uživatele.</summary>
        /// <param name="username">Uživatelské jméno.</param>
        /// <param name="password">Heslo v čistém textu.</param>
        /// <returns>Autentizovaný <see cref="User"/>.</returns>
        public User LogIn(string username, string password)
        {
            using var conn = new SqlConnection(DbConfig.ConnectionString);
            conn.Open();
            const string sql = @"
                SELECT ID, PasswordHash
                FROM Users
                WHERE Username = @username";
            using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@username", username);

            using var reader = cmd.ExecuteReader();
            if (!reader.Read())
            {
                throw new Exception("User not found.");
            }
            var user = new User
            {
                ID = reader.GetInt32(0),
                Username = username,
                PasswordHash = reader.GetString(1)
            };
            if (user.PasswordHash == HashPassword(password))
            {
                return user;
            }
            else
            {
                throw new Exception("Invalid password.");
            }
        }

        /// <summary>Vytvoří SHA-256 hash hesla v Base64.</summary>
        private string HashPassword(string password)
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