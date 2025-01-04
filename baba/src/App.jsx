import React, { useState } from "react";
import axios from "axios";
import ImageConcatenator from "./components/ImageConcatenator";

const App = () => {
  const [image, setImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isolatedObject, setIsolatedObject] = useState(null);
  const [residualBackground, setResidualBackground] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImage(file);
      setProcessedImage(null); // Reset processed image
      setIsolatedObject(null); // Reset isolated object
      setResidualBackground(null); // Reset residual background
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
          responseType: "json", // Expect JSON response with images
        }
      );

      // Extract images from the response
      const { foreground_image, isolated_object, residual_background } =
        response.data;

      setProcessedImage(`data:image/png;base64,${foreground_image}`);
      setIsolatedObject(`data:image/png;base64,${isolated_object}`);
      setResidualBackground(`data:image/png;base64,${residual_background}`);
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
        <div className="grid grid-cols-2 gap-4">
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

          {/* Isolated Object */}
          <div className="w-80 h-80 border-2 border-dashed border-gray-300 bg-gray-200 flex items-center justify-center overflow-hidden">
            {isolatedObject ? (
              <img
                src={isolatedObject}
                alt="Isolated Object"
                className="w-full h-full object-contain"
              />
            ) : (
              <p className="text-gray-500">Background (Isolated Object)</p>
            )}
          </div>

          {/* Residual Background */}
          <div className="w-80 h-80 border-2 border-dashed border-gray-300 bg-gray-200 flex items-center justify-center overflow-hidden">
            {residualBackground ? (
              <img
                src={residualBackground}
                alt="Residual Background"
                className="w-full h-full object-contain"
              />
            ) : (
              <p className="text-gray-500">Residual background</p>
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

      <ImageConcatenator />
    </>
  );
};

export default App;
