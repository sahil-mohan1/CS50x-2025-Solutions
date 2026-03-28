#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

bool check_valid(string s);

int main(int argc, string argv[])
{
    // Make sure the program was run with just one command line argument
    if (argc != 2)
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
    // Make sure argv[1] is a valid key
    if (check_valid(argv[1]))
    {
        // Convert the command line argument to an integer
        string key = argv[1];
        // Prompt the user for a plaintext
        string plaintext = get_string("Plaintext: ");
        // Print the ciphertext
        printf("ciphertext: ");
        for (int i = 0, len = strlen(plaintext); i < len; i++)
        {
            // Logic to handle mixed case plaintext and keys
            if (isupper(plaintext[i]))
            {
                char cipherchar = key[plaintext[i] - 'A'];
                if (isupper(cipherchar))
                {
                    printf("%c", cipherchar);
                }
                else
                {
                    printf("%c", toupper(cipherchar));
                }
            }
            else if (islower(plaintext[i]))
            {
                char cipherchar = key[plaintext[i] - 'a'];
                if (islower(cipherchar))
                {
                    printf("%c", cipherchar);
                }
                else
                    printf("%c", tolower(cipherchar));
            }
            else
                printf("%c", plaintext[i]);
        }
        printf("\n");
        return 0;
    }
    else
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }
}
// Check_valid function checks if the key is valid
bool check_valid(string s)
{
    // Check if the key is 26 characters long
    int n = strlen(s);
    if (n != 26)
    {
        return false;
    }
    for (int i = 0; i < n; i++)
    {
        int count = 0;
        // Check if every character is an alphabet
        if (isalpha(s[i]) == 0)
        {
            return false;
        }
        for (int j = 0; j < n; j++)
        {
            // Ensure that there are no duplicate letters in the key
            if (toupper(s[j]) == toupper(s[i]))
                count++;
        }
        if (count > 1)
            return false;
    }
    return true;
}
