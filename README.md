# FoodFlix: Food recommender App
---------------------------------

Install:
- `git clone https://github.com/jcaravaca/foodflix`
- `cd foodflix`
- Install anaconda: https://conda.io/docs/user-guide/install/index.html
- Create virtual environment: `conda env create -n foodflix -f environment.yml`
- `source activate foodflix`
- `source env.sh`

Run development version locally:
- Set `FLASK_ENV=development` in env.sh
- `source env.sh`
- `./run.sh`
- Your App should be running on: http://0.0.0.0:5000/

Deploy on Heroku:
- Install Heroku: `brew install heroku/brew/heroku`
- `cd foodflix`
- `heroku create foodflix-api-heroku`
- `git push heroku master`
- Your App should be running on: https://foodflix-api-heroku.herokuapp.com/
