# 🎬 CineMatch - Movies Recommendation System

An intelligent movie discovery platform that provides personalized suggestions. This repository contains the complete data processing and model training pipeline, which generates the files needed for the final Streamlit web application.


---
 ## 🚀 About The Project

This project implements a **content-based movie recommendation system** designed to predict user preferences. The core of the recommendation engine uses cosine similarity based on a rich set of semantic and contributor metadata, allowing for nuanced and contextually relevant suggestions.

The entire process is contained within the `Movie Recommendation System.ipynb` notebook, which performs data cleaning, feature engineering, and model creation, ultimately exporting the necessary data files for the interactive Streamlit application.

---
<img width="1919" height="993" alt="CineMatch App Interface" src="https://github.com/user-attachments/assets/230f0af7-735b-4b01-b2e2-7b224bda6c82" />
<img width-="1919" height="995" alt="CineMatch App Details Page" src="https://github.com/user-attachments/assets/65c9babe-efac-483b-9e4b-11b6a19b2bb2" />

---

 ## 🧠 The Recommendation Pipeline

The engine is built on a classic NLP model pipeline:

1.  **Feature Engineering**: Raw data from the TMDB 5000 dataset is cleaned, merged, and consolidated into a composite text "tag" for each movie. This tag holistically represents the film by combining its narrative synopsis with key metadata.

2.  **Text Vectorization**: The text tags are normalized through lowercasing and stemming. They are then converted into a high-dimensional vector space using Scikit-learn's `CountVectorizer`, turning each movie into a numerical fingerprint.

3.  **Similarity Modeling**: A **Cosine Similarity** matrix is computed between all movie vectors. This matrix quantifies the contextual closeness of any two films and serves as the final recommendation model, which is then serialized as a `.pkl` file for the app.
---

 ## ✨ Features of the Final App

* 🧠 **Content-Based Recommendations**: Get instant, relevant movie suggestions.
* 🔥 **Interactive Homepage**: Discover popular movies with a "Top Picks For Today" section.
* 🔎 **Advanced Filtering**: Search the database by genre, actor, director, and more.
* ℹ️ **Detailed Movie View**: Access a rich details page for every movie.
* 📄 **Paginated Results**: Easily browse through large lists of films.
* 🔒 **Secure API Key Management**: Uses Streamlit's secrets for API key handling.

---

## 🛠️ Technologies & Libraries

* 🐍 **Python**
* 📓 **Jupyter Notebook**: For data exploration and model building.
* 🐼 **Pandas**: For data manipulation.
* 🤖 **Scikit-learn**: For `CountVectorizer` and `cosine_similarity`.
* 📚 **NLTK**: For text stemming.
* 🎈 **Streamlit**: For building the final interactive web application.
* 🌐 **Requests**: For making API calls to TMDB.

---

## ⚙️ Setup and Usage

This project has two main parts: running the notebook to generate the model files, and running the Streamlit app.

 ### Part 1: Generating the Model Files

1.  **Prerequisites:**
    * You need Python, Jupyter Notebook, and the TMDB 5000 dataset CSV files (`tmdb_5000_movies.csv` and `tmdb_5000_credits.csv`) placed in the project's root folder.

2.  **Clone the repository and install libraries:**
    ```bash
    git clone [https://github.com/your-username/CineMatch-App.git](https://github.com/your-username/CineMatch-App.git)
    cd CineMatch-App
    pip install -r requirements.txt
    ```

3.  **Run the Jupyter Notebook:**
    * Launch Jupyter Notebook: `jupyter notebook`
    * Open `Movie Recommendation System.ipynb`.
    * Run all the cells from top to bottom. This will perform all the data processing and create the necessary `.pkl` files in your project directory.

### Part 2: Running the Streamlit App

After generating the `.pkl` files, you can run the interactive web app.

1.  **Set up your API Key:**
    * Create a folder named `.streamlit` in the root of your project directory.
    * Inside, create a file named `secrets.toml`.
    * Add your TMDB API key to this file:
        ```toml
        TMDB_API_KEY = "your_actual_api_key_here"
        ```

2.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
