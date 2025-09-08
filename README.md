# 🎬 MovieMatch - Movies Recommendation System  

An intelligent movie discovery platform that provides personalized movie suggestions. This repository contains the complete data processing and model training pipeline, which generates the files needed for the final Streamlit web application.  

Visit here: https://moviematch11.streamlit.app/
---

## 🚀 About The Project  

MovieMatch is a *content-based recommendation system* that predicts user preferences and suggests movies with similar themes, genres, or contributors.  

The recommendation engine is built on cosine similarity applied to a carefully engineered set of metadata, ensuring *contextually relevant and accurate movie matches*.  

---
<img width="1919" height="994" alt="Screenshot 2025-09-08 172408" src="https://github.com/user-attachments/assets/0b63d0d7-f8cc-4811-a2ff-85eb58017ade" />



---


  <img width="1919" height="973" alt="Screenshot 2025-09-08 172454" src="https://github.com/user-attachments/assets/636f38aa-8574-45c8-a44f-88425a90ad3f" />

---

## 🧠 The Recommendation Pipeline  

The system follows a classic NLP-based pipeline:  

1. *Feature Engineering*  
   - Data from TMDB 5000 dataset is cleaned and merged.  
   - Metadata and synopsis are combined into a single *“tag”* for each movie.  

2. *Text Vectorization*  
   - Tags are normalized (lowercasing + stemming).  
   - Converted to numerical vectors using CountVectorizer.  

3. *Similarity Modeling*  
   - A *cosine similarity matrix* computes relationships between all movies.  
   - The model is saved as .pkl files for use in the Streamlit app.  

---

## ✨ Features of the Streamlit App  

* 🧠 *Personalized Recommendations* – Get instant, relevant movie suggestions.  
* 🔥 *Top Picks Section* – Discover trending and popular films.  
* 🔎 *Search Functionality* – Find movies by title.  
* ℹ *Detailed Movie Pages* – Access poster, cast, overview, and more.  
* 📄 *Paginated Results* – Browse large lists of films easily.  
* 🔒 *Secure API Handling* – TMDB API key is stored in secrets.toml.  



<img width="1909" height="994" alt="Screenshot 2025-09-08 172906" src="https://github.com/user-attachments/assets/80e8ad0c-608a-40f6-9417-0565df83917e" />

---

<img width="1919" height="988" alt="Screenshot 2025-08-26 222414" src="https://github.com/user-attachments/assets/936a32ce-89ea-42a8-bd8b-083120fc0ead" />

---

## 🛠 Built With  

* 🐍 Python  
* 📓 Jupyter Notebook – for data exploration & model building  
* 🐼 Pandas – data manipulation  
* 🤖 Scikit-learn – CountVectorizer, cosine_similarity  
* 📚 NLTK – text preprocessing  
* 🎈 Streamlit – web application  
* 🌐 Requests – TMDB API calls  

---

## ⚙ Setup and Usage  

This project has *two main parts*: generating the model and running the app.  

### Part 1: Generate Model Files  

1. Place the dataset files (tmdb_5000_movies.csv, tmdb_5000_credits.csv) in the root folder.  
2. Run the Jupyter Notebook Movie Recommendation System.ipynb.  
3. This will generate the .pkl files (saved in your project directory).  

---

### Part 2: Run the Streamlit App  

1. *API Key Setup*  
   - Create a folder named .streamlit in the project root.  
   - Inside, create secrets.toml file:  
     toml
     TMDB_API_KEY = "your_actual_api_key_here"
       

2. *Run the App*  
   ```bash
   streamlit run app.py


