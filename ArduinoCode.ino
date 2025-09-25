#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>
#include <EEPROM.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Keypad configuration
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// EEPROM and user setup
#define USER_COUNT_ADDR 0
#define USERS_START_ADDR 10
#define MAX_USERS 5
#define TRANSACTION_HISTORY_LENGTH 5

struct User {
  char name[10];
  float balance;
  float transactions[TRANSACTION_HISTORY_LENGTH];
  byte transactionIndex;
};

User users[MAX_USERS];
int userCount = 0;
int currentUserIndex = -1;
bool authenticated = false;

// Function prototypes
void authenticateUser();
void showMainMenu();
void showBalance();
void withdrawMoney();
void depositMoney();
void showMoreOptions();
void showMiniStatement();
void addTransaction(float amount);
float getAmountInput();
char getKeypadInput();
void saveUsersToEEPROM();
void loadUsersFromEEPROM();

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  
  loadUsersFromEEPROM();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome to ATM");
}

void loop() {
  if (!authenticated) {
    authenticateUser();
  } else {
    showMainMenu();
  }
}

// Simulate face authentication
void authenticateUser() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Please Show Face");

  // Simulated face recognition delay
  delay(2000);

  // For demo, automatically authenticate first user
  if (userCount > 0) {
    currentUserIndex = 0;
    authenticated = true;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Welcome ");
    lcd.print(users[currentUserIndex].name);
    delay(2000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Users Found");
    delay(2000);
  }
}

// Main menu navigation
void showMainMenu() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("1.Balance 2.Withdraw");
  lcd.setCursor(0, 1);
  lcd.print("3.Deposit 4.More");

  char option = getKeypadInput();
  switch (option) {
    case '1': showBalance(); break;
    case '2': withdrawMoney(); break;
    case '3': depositMoney(); break;
    case '4': showMoreOptions(); break;
    default:
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Invalid Option");
      delay(2000);
      break;
  }
}

void showBalance() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Balance:");
  lcd.setCursor(0, 1);
  lcd.print(users[currentUserIndex].balance, 2);
  delay(3000);
}

void withdrawMoney() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enter Amount:");

  float amount = getAmountInput();
  if (amount <= 0) return;

  if (users[currentUserIndex].balance >= amount) {
    users[currentUserIndex].balance -= amount;
    addTransaction(-amount);
    saveUsersToEEPROM();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Withdrawn:");
    lcd.setCursor(0, 1);
    lcd.print(amount, 2);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Insufficient Funds");
  }
  delay(3000);
}

void depositMoney() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enter Amount:");

  float amount = getAmountInput();
  if (amount <= 0) return;

  users[currentUserIndex].balance += amount;
  addTransaction(amount);
  saveUsersToEEPROM();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Deposited:");
  lcd.setCursor(0, 1);
  lcd.print(amount, 2);
  delay(3000);
}

void showMoreOptions() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("1.MiniStmt 2.Logout");

  char option = getKeypadInput();
  switch (option) {
    case '1': showMiniStatement(); break;
    case '2': authenticated = false; currentUserIndex = -1; break;
    default:
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Invalid Option");
      delay(2000);
      break;
  }
}

// Show last N transactions
void showMiniStatement() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Mini Statement");

  for (int i = 0; i < TRANSACTION_HISTORY_LENGTH; i++) {
    int index = (users[currentUserIndex].transactionIndex - i - 1 + TRANSACTION_HISTORY_LENGTH) % TRANSACTION_HISTORY_LENGTH;
    float txn = users[currentUserIndex].transactions[index];
    if (txn != 0) {
      lcd.setCursor(0, 1);
      if (txn > 0) lcd.print("+");
      lcd.print(txn, 2);
      delay(2000);
    }
  }
}

// Add a transaction to circular buffer
void addTransaction(float amount) {
  users[currentUserIndex].transactions[users[currentUserIndex].transactionIndex] = amount;
  users[currentUserIndex].transactionIndex = (users[currentUserIndex].transactionIndex + 1) % TRANSACTION_HISTORY_LENGTH;
}

// Get float amount input from keypad
float getAmountInput() {
  String input = "";
  char key;
  while (true) {
    key = keypad.getKey();
    if (key) {
      if (key == '#') break;       // Enter
      else if (key == '*') input = "";  // Clear
      else input += key;
      lcd.setCursor(0, 1);
      lcd.print(input);
    }
  }
  return input.toFloat();
}

// Wait for keypad input
char getKeypadInput() {
  char key = 0;
  while (!key) {
    key = keypad.getKey();
  }
  return key;
}

// Save all users to EEPROM
void saveUsersToEEPROM() {
  EEPROM.write(USER_COUNT_ADDR, userCount);
  for (int i = 0; i < userCount; i++) {
    int addr = USERS_START_ADDR + sizeof(User) * i;
    EEPROM.put(addr, users[i]);
  }
}

// Load all users from EEPROM
void loadUsersFromEEPROM() {
  userCount = EEPROM.read(USER_COUNT_ADDR);
  if (userCount > MAX_USERS) userCount = MAX_USERS;
  for (int i = 0; i < userCount; i++) {
    int addr = USERS_START_ADDR + sizeof(User) * i;
    EEPROM.get(addr, users[i]);
  }
}
