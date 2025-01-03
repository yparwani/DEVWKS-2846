window.addEventListener("load", () => {
  const targetDiv = document.querySelector(".watermark");

  if (targetDiv) {
    const newText = document.createElement("p");
    newText.innerHTML =
      '| Icons by <a href="https://icons8.com/license">Icons8</a>';
    newText.setAttribute(
      "style",
      "font-family: Inter, sans-serif; font-weight: 400; line-height: 1.5; font-size: 12px; color: rgb(189, 189, 189);"
    );
    targetDiv.setAttribute("style", "flex-direction: row;");
    targetDiv.appendChild(newText);
  } else {
    console.error("Target div not found!");
  }
});
