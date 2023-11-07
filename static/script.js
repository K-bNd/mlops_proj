const textGenForm = document.querySelector(".whisper-gen-form");

const get_transcript = async (text) => {
  const inferResponse = await fetch(`transcript`, {
    method: "GET",
    body: {"file": text}, 
  });
  const inferJson = await inferResponse.json();

  return inferJson.output;
};

textGenForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const audioGenInput = document.getElementById("audio-gen-input");
  const textGenParagraph = document.querySelector(".text-gen-output");

  textGenParagraph.textContent = await get_transcript(audioGenInput.value);
});