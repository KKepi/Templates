using System;
using System.Linq;
using System.Text;
using ContactManager.Objects;

namespace ContactManager
{
    class Program
    {
        static void Main(string[] args)
        {
            var credentialProvider = new CredentialProvider();
            User? currentUser = null;
            var controller = new Controller();

            while (true)
            {
                if (currentUser == null)
                {
                    Console.WriteLine("=== Contact Manager ===");
                    Console.WriteLine("1) Register");
                    Console.WriteLine("2) Log In");
                    Console.WriteLine("0) Exit");
                    Console.Write("Select an option: ");
                    var choice = Console.ReadLine();
                    switch (choice)
                    {
                        case "1":
                            Console.Write("Username: ");
                            var regUser = Console.ReadLine()!;
                            Console.Write("Password: ");
                            var regPass = ReadPassword();
                            try
                            {
                                currentUser = credentialProvider.Register(regUser, regPass);
                                Console.WriteLine($"Registered and logged in as {currentUser.Username}");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error: {ex.Message}");
                            }
                            break;
                        case "2":
                            Console.Write("Username: ");
                            var loginUser = Console.ReadLine()!;
                            Console.Write("Password: ");
                            var loginPass = ReadPassword();
                            try
                            {
                                currentUser = credentialProvider.LogIn(loginUser, loginPass);
                                Console.WriteLine($"Logged in as {currentUser.Username}");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error: {ex.Message}");
                            }
                            break;
                        case "0":
                            return;
                        default:
                            Console.WriteLine("Invalid option.");
                            break;
                    }
                }
                else
                {
                    Console.WriteLine($"\n=== Welcome, {currentUser.Username} ===");
                    Console.WriteLine("1) List Contacts");
                    Console.WriteLine("2) Add Contact");
                    Console.WriteLine("3) Copy Contact");
                    Console.WriteLine("4) Delete Contact");
                    Console.WriteLine("5) Undo");
                    Console.WriteLine("6) Redo");
                    Console.WriteLine("7) Log Out");
                    Console.Write("Select an option: ");
                    var choice = Console.ReadLine();
                    switch (choice)
                    {
                        case "1":
                            ListContacts(currentUser);
                            break;
                        case "2":
                            Console.Write("New contact name: ");
                            var newName = Console.ReadLine()!;
                            var newContact = new Contact { Nazev = newName, UserID = currentUser.ID };
                            var addCmd = new AddContact(currentUser, newContact);
                            controller.ExecuteCommand(addCmd);
                            Console.WriteLine("Contact added.");
                            break;
                        case "3":
                            Console.Write("Contact name to copy: ");
                            var copyName = Console.ReadLine()!;
                            var orig = UserContactsFor(currentUser).FirstOrDefault(c => c.Nazev == copyName);
                            if (orig == null)
                            {
                                Console.WriteLine("Contact not found.");
                                break;
                            }
                            var copyCmd = new CopyContact(currentUser, orig);
                            controller.ExecuteCommand(copyCmd);
                            Console.WriteLine("Contact copied.");
                            break;
                        case "4":
                            Console.Write("Contact name to delete: ");
                            var delName = Console.ReadLine()!;
                            var toDelete = UserContactsFor(currentUser).FirstOrDefault(c => c.Nazev == delName);
                            if (toDelete == null)
                            {
                                Console.WriteLine("Contact not found.");
                                break;
                            }
                            var delCmd = new DeleteContact(currentUser, toDelete);
                            controller.ExecuteCommand(delCmd);
                            Console.WriteLine("Contact deleted.");
                            break;
                        case "5":
                            controller.Undo();
                            break;
                        case "6":
                            controller.Redo();
                            break;
                        case "7":
                            currentUser = null;
                            controller = new Controller();
                            Console.WriteLine("Logged out.");
                            break;
                        default:
                            Console.WriteLine("Invalid option.");
                            break;
                    }
                }

                Console.WriteLine();
            }
        }

        static void ListContacts(User user)
        {
            var contacts = new UserContacts(user);
            Console.WriteLine("Your contacts:");
            foreach (var c in contacts)
            {
                Console.WriteLine($"- {c.ID}: {c.Nazev}");
            }
        }

        static IEnumerable<Contact> UserContactsFor(User user)
        {
            return new UserContacts(user).ToList();
        }

        static string ReadPassword()
        {
            var pwd = new StringBuilder();
            ConsoleKeyInfo key;
            while ((key = Console.ReadKey(true)).Key != ConsoleKey.Enter)
            {
                if (key.Key == ConsoleKey.Backspace && pwd.Length > 0)
                {
                    pwd.Length--;
                    Console.Write("\b \b");
                }
                else if (!char.IsControl(key.KeyChar))
                {
                    pwd.Append(key.KeyChar);
                    Console.Write("*");
                }
            }
            Console.WriteLine();
            return pwd.ToString();
        }
    }
}