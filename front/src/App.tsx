import { useState } from "react"

function App() {
  const [output ,setOutput] = useState("")

  const handleChange = (e: any) => {
    setFile(e.target.files[0])
  }

  async function handleSubmit(e: React.FormEvent){
    e.preventDefault()

    if(!file){
      alert('upload file before sending file')
      return
    }

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch('http://0.0.0.0:8000/analize', {
      method: "POST",
      body: formData
    })

    if (!res.body) { alert("No body"); return; }

    const reader = res.body?.getReader()
    const decoder = new TextDecoder()

    let buffer = ""

    while(true){
      const {value, done} = await reader.read()
      if(done) break;

      buffer += decoder.decode(value, {stream: true})

      const chunks = buffer.split("\n\n")

      buffer = chunks.pop() ?? ""

      for(const chunk of chunks){

        const line = chunk.split("\n").find(l => l.startsWith("data:"))

        if(!line) continue;

        const payload = line.slice("data:".length)
        if (payload === "[DONE]") {
          return;
        }

        setOutput(prev => prev + payload);
      }

    }
  }

  const [file, setFile] = useState<File | null>(null)
  return (
    <div className="">
      <p>Upload pdf</p>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleChange} className="border boder-black p-2"/>
        <button type="submit">Submit</button>
      </form>
      {output}
    </div>
  )
}

export default App
