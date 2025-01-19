import React, { useState } from "react";
import axios from "axios";

const AddTextBehindObject = () => {
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");
  const [fontSize, setFontSize] = useState(40);
  const [textColor, setTextColor] = useState("#000000");
  const [textPosition, setTextPosition] = useState({ x: 50, y: 50 });
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image || !text) {
      alert("Please upload an image and enter some text.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("image", image);
    formData.append("text", text);
    formData.append("font_size", fontSize);
    formData.append("text_color", textColor);
    formData.append("x_position", textPosition.x);
    formData.append("y_position", textPosition.y);

    try {
      const response = await axios.post(
        "http://localhost:5000/add-text-behind",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      // Decode Base64 response and create a preview URL
      const base64Image = response.data.final_image;
      const imageUrl = `data:image/png;base64,${base64Image}`;
      setPreviewUrl(imageUrl);
    } catch (error) {
      console.error("Error processing image:", error);
      alert("Failed to process the image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      <h1 className="text-2xl font-bold mb-6">Add Text Behind Object</h1>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col items-center space-y-4"
      >
        <div className="w-full max-w-md">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Upload Image
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>

        <div className="w-full max-w-md">
          <label className="block text-sm font-medium text-black mb-1">
            Enter Text
          </label>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to add behind object"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="w-full max-w-md">
          <label className="block text-sm font-medium text-black mb-1">
            Font Size ({fontSize}px)
          </label>
          <input
            type="range"
            min="10"
            max="100"
            value={fontSize}
            onChange={(e) => setFontSize(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        <div className="w-full max-w-md">
          <label className="block text-sm font-medium text-black mb-1">
            Text Color
          </label>
          <input
            type="color"
            value={textColor}
            onChange={(e) => setTextColor(e.target.value)}
            className="w-full"
          />
        </div>

        <div className="w-full max-w-md">
          <label className="block text-sm font-medium text-black mb-1">
            Text Position (X: {textPosition.x}%, Y: {textPosition.y}%)
          </label>
          <div className="flex space-x-4">
            <input
              type="range"
              min="0"
              max="100"
              value={textPosition.x}
              onChange={(e) =>
                setTextPosition({
                  ...textPosition,
                  x: parseInt(e.target.value),
                })
              }
              className="w-full"
            />
            <input
              type="range"
              min="0"
              max="100"
              value={textPosition.y}
              onChange={(e) =>
                setTextPosition({
                  ...textPosition,
                  y: parseInt(e.target.value),
                })
              }
              className="w-full"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-indigo-300"
        >
          {loading ? "Processing..." : "Submit"}
        </button>
      </form>

      {previewUrl && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Processed Image:</h2>
          <img
            src={previewUrl}
            alt="Processed"
            className="w-full max-w-md rounded-lg shadow-lg"
          />
        </div>
      )}
    </div>
  );
};

export default AddTextBehindObject;
