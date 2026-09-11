export const SAMPLE_SNIPPETS = {
  python_fib: {
    title: "Python: Broken Fibonacci & Recursion Limit",
    language: "python",
    code: `def fibonacci(n):
    # Bug: Missing base case for n <= 0, causing infinite recursion
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

print("Result:", fibonacci(0))`,
  },
  js_async: {
    title: "JS: Unhandled Promise & Race Condition",
    language: "javascript",
    code: `async function fetchUserData(userId) {
  let user = null;
  // Bug: Missing await on asynchronous database query
  database.find({ id: userId }).then(res => {
    user = res.data;
  });
  // Returns null before promise resolves
  return user.profile.name;
}`,
  },
  python_security: {
    title: "Python: SQL Injection Flaw",
    language: "python",
    code: `def get_user_by_email(cursor, email):
    # Vulnerability: Direct string interpolation into raw SQL query
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchone()`,
  },
};
