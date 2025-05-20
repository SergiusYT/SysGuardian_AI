let chatDiv = document.getElementById("chat");
let firstMessageSent = false;

let terminalDebeEstarOculta = false;



const preloadImage = new Image();
preloadImage.src = "img/logo_neon.png";  

let nombreUsuario = "Usuario"; // valor por defecto

eel.get_username()(username => {
  document.getElementById("user-name").textContent = username;
  nombreUsuario = username;
});


// 🧹 Ocultar el mensaje de bienvenida
function hideWelcome() {
  const welcome = document.getElementById("welcome");
  const logo = document.querySelector(".welcome-logo");

  if (welcome) {
    welcome.classList.add("fade-out");
  }
  if (logo) {
    logo.classList.add("fade-out");
  }

  setTimeout(() => {
    if (welcome) welcome.remove();
    if (logo) logo.remove();
  }, 1000);
}


// ✅ Envío de mensaje con integración del ocultamiento del mensaje
document.getElementById("send-button").addEventListener("click", async () => {
  const input = document.getElementById("user-input");
  const prompt = input.value.trim();
  if (!prompt) return;

  if (!firstMessageSent) {
    document.getElementById("chat-logo").style.display = "block";
    firstMessageSent = true;
    hideWelcome();
  }

  input.value = "";
  
  await eel.enviar_mensaje_stream(prompt)();
});

// Enter como disparador
document.getElementById("user-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("send-button").click();
  }
});

// 🔁 Render inicial del historial
async function renderChat() {
  const html = await eel.obtener_historial()();
  const tempContainer = document.createElement("div");
  tempContainer.innerHTML = html;

  [...tempContainer.children].forEach(child => {
    chatDiv.appendChild(child);
  });

  chatDiv.scrollTop = chatDiv.scrollHeight;
}


// 📩 Mostrar burbuja de usuario
eel.expose(nuevo_mensaje_usuario);
function nuevo_mensaje_usuario(html) {
    const inicial = nombreUsuario.charAt(0).toUpperCase();

    const container = document.createElement("div");
    container.className = "bubble-container";
    container.style.justifyContent = "flex-end";

    const bubble = document.createElement("div");
    bubble.className = "bubble user";
    bubble.innerHTML = html;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = inicial;

    container.appendChild(bubble);
    container.appendChild(avatar);

    chatDiv.appendChild(container);
    chatDiv.scrollTop = chatDiv.scrollHeight;
}


// 🤖 Inicia burbuja de respuesta IA
eel.expose(iniciar_respuesta_ai);
function iniciar_respuesta_ai(idBurbuja) {
  terminalDebeEstarOculta = false;

  const container = document.createElement("div");
  container.className = "bubble-container writing"; // <-- ESTA CLASE DIFERENCIA QUE ESTÁ ESCRIBIENDO
  container.id = "typing-bubble";

  const avatar = document.createElement("div");
  avatar.className = "avatar";

  const img = preloadImage;
  img.classList.add("avatar-img");
  avatar.appendChild(img);

  const template = document.getElementById("ia-avatar-template");
  if (template) {
      const imgTemp = template.content.firstElementChild.cloneNode(true);
      imgTemp.classList.add("temp-avatar");
      avatar.appendChild(imgTemp);
  } else {
      avatar.textContent = "🤖";
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble ai";
  bubble.innerHTML = `<b>🤖 SysGuardian AI:</b><br><div class="contenido-respuesta" id="contenido-${idBurbuja}"></div>`;

  container.appendChild(avatar);
  container.appendChild(bubble);

  chatDiv.appendChild(container);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}



// ❌ Eliminar burbuja "escribiendo"
eel.expose(hide_typing_bubble);
function hide_typing_bubble() {
  const typingBubble = document.getElementById("typing-bubble");
  if (typingBubble) {
    const contenido = typingBubble.querySelector(".contenido-respuesta");
    
    // Guardar el HTML ya generado
    let respuestaTemporal = contenido ? contenido.innerHTML : "";
    
    if (contenido) contenido.innerHTML = "";  // Borra el texto temporal
    typingBubble.removeAttribute("id"); // Evita duplicados

    // Restaurar lo que se había generado
    if (contenido) contenido.innerHTML = respuestaTemporal;
  }
}

function actualizarMensajeInformativo(idBurbuja, mensaje) {
    const contenedor = document.getElementById(`contenido-${idBurbuja}`);
    if (contenedor) {
        contenedor.innerHTML = `<i>${mensaje}<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></i>`;
    }
}

eel.expose(actualizar_mensaje_estado);
function actualizar_mensaje_estado(mensaje, idBurbuja) {
    actualizarMensajeInformativo(idBurbuja, mensaje);
}


// ✍️ Mostrar contenido palabra por palabra
eel.expose(actualizar_respuesta_ai);
function actualizar_respuesta_ai(html, idBurbuja) {
  const contenido = document.getElementById("contenido-" + idBurbuja);
  if (contenido) {
    contenido.innerHTML = html + '<span class="typing-cursor" id="cursor-' + idBurbuja + '"></span>';

    // SOLO bajar el scroll si ya estaba abajo
    const isNearBottom = chatDiv.scrollHeight - chatDiv.scrollTop <= chatDiv.clientHeight + 100;
    if (isNearBottom) {
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }
  }
}


function mostrarAvatarFlotante(conMensaje = "¡Estoy pensando...!") {
  const avatarFlotante = preloadImage.cloneNode(true);
  avatarFlotante.classList.add("avatar-flotante");

  const burbujaMensaje = document.createElement("div");
  burbujaMensaje.className = "mensaje-avatar-flotante";
  burbujaMensaje.innerText = conMensaje;

  const contenedorFlotante = document.createElement("div");
  contenedorFlotante.className = "contenedor-avatar-msg";
  contenedorFlotante.appendChild(avatarFlotante);
  contenedorFlotante.appendChild(burbujaMensaje);

  document.body.appendChild(contenedorFlotante);

  setTimeout(() => {
    contenedorFlotante.classList.add("fade-out");
    setTimeout(() => contenedorFlotante.remove(), 1000);
  }, 2500);
}


// ✅ Finalizar la respuesta
eel.expose(finalizar_respuesta_ai);
function finalizar_respuesta_ai(cierre, idBurbuja) {
  const contenido = document.getElementById("contenido-" + idBurbuja);
  const cursor = document.getElementById("cursor-" + idBurbuja);

  if (cursor) cursor.remove();
  if (contenido) {
    contenido.innerHTML += cierre;
    contenido.removeAttribute("id");
  }

  const bubbleContainer = contenido.closest(".bubble-container");
  const avatarDiv = bubbleContainer?.querySelector(".avatar");

  if (avatarDiv) {
    // Eliminar cualquier imagen previa para evitar duplicados
    avatarDiv.querySelectorAll("img").forEach(el => el.remove());

    // Crear y agregar el avatar final con animación
    const img = preloadImage.cloneNode(true);
    img.classList.add("avatar-img", "final-avatar");
    mostrarAvatarFlotante("¡Listo!");
    avatarDiv.appendChild(img);

  }

  // 💡 Aquí quitamos la clase "writing" y ponemos "done"
  if (bubbleContainer) {
    bubbleContainer.classList.remove("writing");
    bubbleContainer.classList.add("done");
  }

}

function typeCommandLine(container, text, delay = 5) {
    container.innerHTML = "";
    let i = 0;

    const interval = setInterval(() => {
        container.innerHTML += text.charAt(i);
        i++;
        if (i >= text.length) clearInterval(interval);
    }, delay);
}



eel.expose(mostrar_consola_comando);
function mostrar_consola_comando(cmd, salida = "") {
    if (terminalDebeEstarOculta) return;

    const ultAiBubble = [...document.querySelectorAll(".bubble.ai")].pop();
    if (!ultAiBubble) return;

    let termBox = ultAiBubble.querySelector(".terminal-box");

    if (!termBox) {
        termBox = document.createElement("div");
        termBox.className = "terminal-box";
        termBox.innerHTML = `
          <div class="terminal-head">Terminal</div>
          <div class="terminal-body"></div>`;
        ultAiBubble.appendChild(termBox); // ✅ ahora está dentro de la burbuja
    }

    const termBody = termBox.querySelector(".terminal-body");

    // Detecta tipo de comando
    const isWin = /(?:dir|cls|copy|ipconfig|netstat|wmic|powershell|query|🪟)/i.test(cmd);
    const systemClass = isWin ? "terminal-win" : "terminal-linux";
    const prompt = isWin ? `C:\\Users\\${nombreUsuario}>` : `${nombreUsuario}@host:~$`;

    // Limpiar clases previas antes de aplicar la nueva
    termBox.classList.remove("terminal-linux", "terminal-win", "terminal-hidden");
    termBox.classList.add(systemClass);

    // Limpiar contenido anterior (como lo hacías antes)
    termBody.innerHTML = "";

    // Crear bloque de comando
    const block = document.createElement("div");
    block.className = "command-block";
    block.innerHTML = `
      <span class="${isWin ? 'prompt-win' : 'prompt-linux'}">${prompt}</span><span class="cmd-anim"></span>
      ${salida ? `<div class="output">${salida}</div>` : ""}
    `;

    termBody.appendChild(block);

    const animSpan = block.querySelector(".cmd-anim");
    typeCommandLine(animSpan, cmd);

    // 🟢 Forzar scroll al final
    setTimeout(() => {
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }, 50);
}



eel.expose(mostrar_consola_codigo);

function mostrar_consola_codigo(cmd, salida = "") {
    if (terminalDebeEstarOculta) return;

    const ultAiBubble = [...document.querySelectorAll(".bubble.ai")].pop();
    if (!ultAiBubble) return;

    let termBox = ultAiBubble.querySelector(".terminal-box");

    if (!termBox) {
        termBox = document.createElement("div");
        termBox.className = "terminal-box";
        termBox.innerHTML = `
          <div class="terminal-head">Terminal</div>
          <div class="terminal-body"></div>`;
        ultAiBubble.appendChild(termBox);
    }

    const termBody = termBox.querySelector(".terminal-body");

    // Detecta tipo de comando
    const isWin = /(?:dir|cls|copy|ipconfig|netstat|wmic|powershell|query|🪟)/i.test(cmd);
    const systemClass = isWin ? "terminal-win" : "terminal-linux";
    const prompt = isWin ? `C:\\Users\\${nombreUsuario}>` : `${nombreUsuario}@host:~$`;

    // Limpiar clases previas antes de aplicar la nueva
    termBox.classList.remove("terminal-linux", "terminal-win", "terminal-hidden");
    termBox.classList.add(systemClass);

    // ❌ Ya no borramos termBody.innerHTML aquí

    // Crear bloque de comando
    const block = document.createElement("div");
    block.className = "command-block";
    block.innerHTML = `
      <span class="${isWin ? 'prompt-win' : 'prompt-linux'}">${prompt}</span><span class="cmd-anim"></span>
      ${salida ? `<div class="output">${salida}</div>` : ""}
    `;

    termBody.appendChild(block);

    const animSpan = block.querySelector(".cmd-anim");
    typeCommandLine(animSpan, cmd);

    setTimeout(() => {
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }, 50);
}



eel.expose(ocultar_consola);
function ocultar_consola() {
  terminalDebeEstarOculta = true;

  document.querySelectorAll(".terminal-box").forEach(box => {
    box.classList.add("terminal-hidden");
    const body = box.querySelector(".terminal-body");
    if (body) body.textContent = "";
  });
}



renderChat();