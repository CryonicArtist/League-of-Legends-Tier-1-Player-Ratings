%% LoL Player Rating Analysis Program

% --- Configuration ---
datafile = 'LoLData.xlsx - Sheet1.csv';
minGames = 15; % Minimum games played to be included in the rating

% Define the stats we will use for the rating
% Make sure these names match the CSV headers exactly
keyStats = {
    'WinRate', ...
    'KDA', ...
    'GPM', ...
    'DMG_', ...  % Note: Header in file is "DMG%" which MATLAB imports as "DMG_"
    'VSPM', ...
    'GD_15'      % Note: Header in file is "GD@15" which MATLAB imports as "GD_15"
};

% Define the weights for each stat (must sum to 1)
% Order must match keyStats
weights = [
    0.25, ...  % WinRate
    0.25, ...  % KDA
    0.15, ...  % GPM
    0.15, ...  % DMG%
    0.10, ...  % GD@15
    0.10      % VSPM
];

% --- 1. Load and Clean Data ---
fprintf('Loading data from %s...\n', datafile);

% Set options to handle the data file
opts = detectImportOptions(datafile);

% Rename the first variable to 'Player'
opts.VariableNames{1} = 'Player'; 

% Remove the second, empty 'NaN' column (imported as 'Var2')
opts = setvartype(opts, 'Var2', 'char'); % Read as char to ignore
opts = setvaropts(opts, 'Var2', 'TreatAsMissing', 'NaN');

% Tell MATLAB to treat the '-' character as missing data
opts.MissingRule = 'treatas';
opts.TreatAsMissing = {'-', 'NaN'};

% Import the data
try
    data = readtable(datafile, opts);
catch ME
    fprintf('Error reading file: %s\n', ME.message);
    fprintf('Please make sure the file is in the same directory.\n');
    return;
end

% Remove the junk column
data.Var2 = [];

% --- 2. Filter and Prepare Data ---

% Filter by minimum games played
originalCount = height(data);
data(data.Games < minGames, :) = [];
fprintf('Filtered %d players with fewer than %d games. Analyzing %d players.\n', ...
        originalCount - height(data), minGames, height(data));

% Select the key stats for analysis
statsTable = data(:, keyStats);

% Convert table to a numeric array
statsArray = statsTable{:,:};

% Clean Data: Fill any missing (NaN) values with the mean of that column
statsArray = fillmissing(statsArray, 'mean');

% --- 3. Normalize Stats (Z-score) ---
% This rescales all stats to a common scale
normalizedStats = zscore(statsArray);

% --- 4. Calculate Weighted Score ---
% Multiply the normalized stats by their weights and sum them up
% This results in a single composite Z-score for each player
compositeScore = normalizedStats * weights';

% --- 5. Rescale to 0-100 Rating ---
% Rescale the composite score to a familiar 0-100 "FIFA-style" rating
minScore = min(compositeScore);
maxScore = max(compositeScore);
playerRating = 100 * (compositeScore - minScore) / (maxScore - minScore);

% --- 6. Display Results ---
% Add the new PlayerRating column to our table
data.PlayerRating = playerRating;

% Sort the table to find the best players
sortedData = sortrows(data, 'PlayerRating', 'descend');

% Display the Top 20 players
fprintf('\n--- Top 20 Highest Rated Players ---\n');
disp(sortedData(1:20, {'Player', 'PlayerRating', 'Games', 'KDA', 'WinRate'}));