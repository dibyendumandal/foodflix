## env		: Create a conda environment required for the analysis
CONDA_REQUIREMENTS=environment.yml
CONDA_ROOT=$(shell conda info -s | grep CONDA_ROOT | cut -f2 -d ' ')
ENV=$(shell head -n 1 $(CONDA_REQUIREMENTS) | cut -f2 -d ' ')
env : $(CONDA_REQUIREMENTS)
	@echo "Installing conda environment '$(ENV)'."
	@if [ -d "$(CONDA_ROOT)/envs/$(ENV)" ]; then \
		echo "\nConda environment '$(ENV)' exists. Reinstalling now."; \
		conda env remove -n $(ENV); \
	fi
	conda env create -f $(CONDA_REQUIREMENTS)


.PHONY : %-nb
TIMEOUT=600
NOTEBOOKDIR=notebooks/
%-nb: $(NOTEBOOKDIR)%.ipynb
	@jupyter nbconvert \
		--ExecutePreprocessor.timeout=$(TIMEOUT) \
		--ExecutePreprocessor.kernel_name=python \
		--to notebook \
		--execute $< \
		--output $(patsubst $(NOTEBOOKDIR)%.ipynb, %.ipynb, $<)

## data		: Preprocess data
data : 00.0-kjb-Data_Preprocessing-nb

## clean 	: Remove intermediate files
clean :
	rm FoodFlix/static/data/*.csv

## uninstall	: Uninstall the conda environment
uninstall :
	conda env remove -n $(ENV) -y

help : Makefile
	@sed -n 's/^##//p' $<

.PHONY : env data clean uninstall help
