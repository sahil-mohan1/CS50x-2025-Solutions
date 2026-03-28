#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool only_digits(string s);
char rotate(char c, int key);

int main(int argc, string argv[])
{
    // Make sure the program was run with just one command line argument
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // Make sure argv[1] consists of digits only
    if (only_digits(argv[1]))
    {
        // Convert the command line argument to an integer
        int key = atoi(argv[1]);
        // Prompt the user for plaintext
        string plaintext = get_string("Plaintext: ");
        printf("Ciphertext: ");
        for (int i = 0, len = strlen(plaintext); i < len; i++)
        {
            // Call the rotate function to encrypt each character
            printf("%c", rotate(plaintext[i], key));
        }
        printf("\n");
        return 0;
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
}
// Return true if argv[1] consists of digits only, false otherwise
bool only_digits(string s)
{
    for (int i = 0, n = strlen(s); i < n; i++)
    {
        if (isdigit(s[i]) == 0)
        {
            return false;
        }
    }
    return true;
}

char rotate(char c, int key)
{
    // If the character is a letter, add the key to it and wrap around if necessary
    if (isalpha(c))
    {
        if (islower(c))
        {
            c -= 'a';
            return (((c + key) % 26) + 'a');
        }
        else
        {
            c -= 'A';
            return (((c + key) % 26) + 'A');
        }
    }
    // If the character is not a letter, return it unchanged
    else
        return c;
}
