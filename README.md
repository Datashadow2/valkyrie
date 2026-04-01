Here’s the concise set of **rules and conventions for writing any Valkyrie script** based on the final interpreter and weapons system:

---

### 1. **Variables**

* Declared with `let`:

  ```vk
  let x = 10
  let name = "Valkyrie"
  ```
* Variables are **dynamically typed**.
* `_result` stores the last function/call result automatically.

---

### 2. **Expressions**

* Simple math: `+`, `-`, `*`, `/`

  ```vk
  let total = score + bonus
  ```
* Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
* **No automatic complex expression parsing**: `(a+b)*c` may fail; use intermediate variables.
* **Slicing / indexing** requires assigning to a variable:

  ```vk
  call call_lang python "os" "listdir" "."
  call str _result
  let first3 = _result[:3]
  ```

---

### 3. **Printing / Output**

* `print` prints evaluated expressions:

  ```vk
  print "Score: " + str(total)
  ```
* All interpreter output (prompt, debug messages) is **green by default**.
* Errors are **blue**, warnings optional.

---

### 4. **Conditionals**

* Single-line:

  ```vk
  if total >= 90 then print "Pass"
  ```
* Multi-line:

  ```vk
  if total >= 90
      print "Pass"
      call color_print "Congrats!" green
  endif
  ```

---

### 5. **Functions**

* Define with `fn` / `endfn`:

  ```vk
  fn double n
      mul n 2
      return n
  endfn
  ```
* Local variables are temporary, globals restored after call.
* `_result` captures return value if used outside function.

---

### 6. **Calls to Weapons / External Languages**

* Call built-in weapon:

  ```vk
  call file_write "test.txt" "Hello"
  ```
* Cross-language:

  ```vk
  call call_lang python "random" "randint" 1 100
  call call_lang python "os" "listdir" "."
  ```
* Rust, C, Go, Java all go through `call_lang` wrappers (compile if needed).

---

### 7. **Stack Operations**

* Push / pop variables:

  ```vk
  push x
  pop y
  ```

---

### 8. **Control**

* `goto` for labels:

  ```vk
  start:
      print "Loop"
      goto start
  ```
* `hlt` to halt execution.
* `_result` always captures the last call or computation result.

---

### 9. **User Input**

* Use `call input "Prompt"` (red by default):

  ```vk
  call input "Enter your name: "
  print "Hello, " + _result
  ```

---

### 10. **Best Practices / Gotchas**

* Convert types explicitly with `call str`, `call int`, etc. before concatenation.
* Always assign complex expressions to variables before using them in prints or calls.
* Avoid nested operators; break into steps.
* Errors are displayed in blue; use `call color_print` for emphasis.

---

Do you want me to do that?
