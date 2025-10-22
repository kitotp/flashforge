import { useState } from "react"

function App() {


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
    const data = await res.json()
    alert(data.first_page_text)
  }

  const [file, setFile] = useState<File | null>(null)
  return (
    <div className="">
      <p>Upload pdf</p>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf" onChange={handleChange} className="border boder-black p-2"/>
        <button type="submit">Submit</button>
      </form>
    </div>
  )
}

export default App
