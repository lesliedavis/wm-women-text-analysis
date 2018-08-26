#### File Last Updated: 8/21/2018 by Leslie Davis
#### File purpose: Manipulating data for calculations and visualizations

# % matplotlib inline
import pandas as pd
import csv


###### Reading in csv data ############
my_df = pd.read_csv('final.csv', header =None, quoting=csv.QUOTE_NONE)
my_df

##### Renaming the columns of the dataframe ######
my_df.columns = ['Word', 'Author', 'Gender', 'Year', 'Month-Day', 'M-Code', 'Org', 'Topics', 'Freq in Source','Total Word Count/Source', 'Concord.', 'Collo.']
my_df.head()

##### Creating a subsets ###########
rape_subset = my_df[my_df['Word']=='rape'] #this word is used as a test case, looking for duplicate entries for the same source in dataframe
rape_subset #checking frequencies
rape_subset['Freq in Source'].sum() #summing their frequencies to find how often appeared across all sources

chair_subset = my_df[my_df['Word']=='chairman']
chair_subset

#### Calculating the total frequencies of each word across all sources ####
f = open('final.csv')
csv_f = csv.reader(f)

master = {}
for line in csv_f:
        if line[0] in master:
            master[line[0]] += int(line[8])
        else:
            master[line[0]]= int(line[8])


#### Placing master frequencies in the dataframe ###########
words_col = my_df['Word']
my_df['Overall Frequency'] = words_col.map(master)
my_df['Overall Frequency'] = my_df['Overall Frequency'].fillna(0.0).astype(int) #converts the floats to ints, replaces NaNs if necessary
# my_df.head()

####### Changing variable datatypes ############
my_df['Gender'] = my_df['Gender'].astype('category') ## converted gender to a categorical variable
my_df['Gender']
my_df.dtypes #checks datatypes for each series

####### Calculations #############
my_df['Percent of Word in Source']= (my_df['Freq in Source']/my_df['Total Word Count/Source'])*100 # Creating new column for Word in Source %
my_df.head(50)

##### Exporting final csv ##############
my_df.to_csv('csv_for_tableau.csv', encoding='utf-8', index=False, na_rep="NaN") #removes dataframe indexes, retains NaNs for missing data
