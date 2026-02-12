//default
//const userPref = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"
//const currentTheme = localStorage.getItem("theme") ?? userPref
//document.documentElement.setAttribute("saved-theme", currentTheme)

//@@KURT - forced dark mode
const userPref = localStorage.getItem("theme")
// 시스템 설정을 무시하고 싶다면 아래처럼 수정하세요.
const systemPref = "dark" // 원래는 window.matchMedia... 로직이 있던 곳입니다.
const currentTheme = "dark" // userPref ?? systemPref 대신 "dark"로 강제 고정

// 테마 적용 로직
document.documentElement.setAttribute("saved-theme", currentTheme)


const emitThemeChangeEvent = (theme: "light" | "dark") => {
  const event: CustomEventMap["themechange"] = new CustomEvent("themechange", {
    detail: { theme },
  })
  document.dispatchEvent(event)
}

document.addEventListener("nav", () => {
  const switchTheme = () => {
    const newTheme =
      document.documentElement.getAttribute("saved-theme") === "dark" ? "light" : "dark"
    document.documentElement.setAttribute("saved-theme", newTheme)
    localStorage.setItem("theme", newTheme)
    emitThemeChangeEvent(newTheme)
  }

  const themeChange = (e: MediaQueryListEvent) => {
    const newTheme = e.matches ? "dark" : "light"
    document.documentElement.setAttribute("saved-theme", newTheme)
    localStorage.setItem("theme", newTheme)
    emitThemeChangeEvent(newTheme)
  }

  for (const darkmodeButton of document.getElementsByClassName("darkmode")) {
    darkmodeButton.addEventListener("click", switchTheme)
    window.addCleanup(() => darkmodeButton.removeEventListener("click", switchTheme))
  }

  // Listen for changes in prefers-color-scheme
  const colorSchemeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
  colorSchemeMediaQuery.addEventListener("change", themeChange)
  window.addCleanup(() => colorSchemeMediaQuery.removeEventListener("change", themeChange))
})
