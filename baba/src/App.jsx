import React, { useState } from "react";
import axios from "axios";
import ImageConcatenator from "./components/ImageConcatenator";

const App = () => {
  const [image, setImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [backgroundImage, setBackgroundImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImage(file);
      setProcessedImage(null); // Reset processed image
      setBackgroundImage(null); // Reset background image
    }
  };

  const handleRemoveBackground = async () => {
    if (!image) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("image", image);

    try {
      const response = await axios.post(
        "http://localhost:5000/remove-background",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          responseType: "json", // Expect JSON response with both images
        }
      );

      // Extract foreground and background images from response
      const { foreground_image, background_image } = response.data;
      console.log(foreground_image, background_image);
      setProcessedImage(`data:image/png;base64,${foreground_image}`);
      setBackgroundImage(`data:image/png;base64,${background_image}`);
    } catch (error) {
      console.error("Error removing background:", error);
      alert("Failed to process the image. Check the server or input image.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Free Background Remover</h1>

      {/* Upload Image */}
      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        className="mb-4"
      />

      {/* Image Placeholders */}
      <div className="flex gap-4">
        {/* Original Image */}
        <div className="w-80 h-80 border-2 border-dashed border-gray-300 bg-gray-200 flex items-center justify-center overflow-hidden">
          {image ? (
            <img
              src={URL.createObjectURL(image)}
              alt="Original"
              className="w-full h-full object-contain"
            />
          ) : (
            <p className="text-gray-500">Original image</p>
          )}
        </div>

        {/* Foreground Image */}
        <div className="w-80 h-80 border-2 border-dashed border-gray-300 bg-gray-200 flex items-center justify-center overflow-hidden">
          {processedImage ? (
            <img
              src={processedImage}
              alt="Foreground"
              className="w-full h-full object-contain"
            />
          ) : (
            <p className="text-gray-500">Foreground image</p>
          )}
        </div>

        {/* Background Image */}
        <div className="w-80 h-80 border-2 border-dashed border-gray-300 bg-gray-200 flex items-center justify-center overflow-hidden">
          {backgroundImage ? (
            <img
              src={backgroundImage}
              alt="Background"
              className="w-full h-full object-contain"
            />
          ) : (
            <p className="text-gray-500">Background image</p>
          )}
        </div>
      </div>

      {/* Buttons */}
      <button
        onClick={handleRemoveBackground}
        disabled={!image || loading}
        className={`mt-4 py-2 px-6 bg-blue-500 text-white rounded-md ${
          loading ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-600"
        }`}
      >
        {loading ? "Processing..." : "Remove Background"}
      </button>
    </div>


<ImageConcatenator/>
</>  
);

};

export default App;
