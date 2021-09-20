library(keras)
library(dplyr)
library(purrr)

setwd('/home/aw/Documents/w/py/scrape-recipes/texts')
f.names = list.files(pattern = '*.txt')

all.recipes = list()
all.sentences = character()
all.titles = character()
for (f.name in f.names[1:3000]) {
  f.lines = readLines(f.name, warn = F)
  if (f.lines[1] %in% all.titles) next
  all.titles = c(all.titles, f.lines[1])
  methodIdx = which(f.lines == '==========')[2] + 1
  methodLines = f.lines[methodIdx:length(f.lines)]
  sentences = trimws(unlist(strsplit(methodLines, "[.][ ]|[!][ ]")))
  sentences = sentences[sentences != '' & nchar(sentences) > 1]
  sent.clean = tolower(paste(sub("[.]$|[!]$", "", sentences), '.', sep=''))
  all.sentences = c(all.sentences, sent.clean)
  all.recipes = c(all.recipes, list(sent.clean))
}
  # sort(table(all.sentences), decreasing=T)[50:100]
# length(sort(table(unlist(strsplit(all.sentences, ""))), decreasing=T))
# code.factor = as.factor(unique(unlist(strsplit(all.sentences, ''))))
# encode  = Vectorize(function(string) match(unlist(strsplit(string, '')), code.factor), USE.NAMES = F)
# decode = Vectorize(function(nums) paste(code.factor[nums], collapse=''), USE.NAMES = F)
# encode(all.sentences)
text.block = all.sentences %>% 
  paste(collapse=' ') %>%
  strsplit('') %>%
  unlist()


chars <- text.block %>%
  unique() %>%
  sort()

maxlen = 40
dataset <- map(seq(1, length(text.block) - maxlen - 1, by = 14), 
          ~list(sentence = text.block[.x:(.x + maxlen - 1)], next_char = text.block[.x + maxlen]))
dataset <- transpose(dataset)

x <- array(0, dim = c(length(dataset$sentence), maxlen, length(chars)))
y <- array(0, dim = c(length(dataset$sentence), length(chars)))

for(i in 1:length(dataset$sentence)){
  x[i,,] <- sapply(chars, function(x) as.integer(x == dataset$sentence[[i]]))
  y[i,] <- as.integer(chars == dataset$next_char[[i]])
}
 

model <- keras_model_sequential()

model %>%
  layer_lstm(128, input_shape = c(maxlen, length(chars))) %>%
  layer_dense(length(chars)) %>%
  layer_activation("softmax")

optimizer <- optimizer_rmsprop(learning_rate = 0.01)

model %>% compile(loss = "categorical_crossentropy", optimizer = optimizer)

model %>% fit(x, y, batch_size=128, epochs=6)

runPrediction = function() {
  start.idx <- sample(1:(length(text.block) - maxlen), size = 1)
  cur.sentence <- text.block[start.idx:(start.idx + maxlen - 1)]
  generated = ''
  gen.length = 400
  pb = txtProgressBar(min = 1, max = gen.length, initial = 1)
  for(i in 1:gen.length){
    setTxtProgressBar(pb,i)
    x.pred <- sapply(chars, function(x) as.integer(x == cur.sentence))
    x.pred <- array_reshape(x.pred, c(1, dim(x.pred)))
    
    preds <- predict(model, x.pred)
    next_char <- sample(chars, 1, prob=(preds^2 / sum(preds^2)))
    # next_char <- chars[next_index]
    generated <- paste(generated, next_char, sep = "")
    cur.sentence <- c(cur.sentence[-1], next_char)
  }
  close(pb)
  generated
}
runPrediction()


# start.idx <- sample(1:(length(text.block) - maxlen), size = 1)
# cur.sentence <- text.block[start.idx:(start.idx + maxlen - 1)]
# generated = ''
# gen.length = 400
# pb = txtProgressBar(min = 1, max = gen.length, initial = 1)
# for(i in 1:gen.length){
#   setTxtProgressBar(pb,i)
#   x.pred <- sapply(chars, function(x) as.integer(x == cur.sentence))
#   x.pred <- array_reshape(x.pred, c(1, dim(x.pred)))
#   
#   preds <- predict(model, x.pred)
#   next_char <- sample(chars, 1, prob=preds)
#   # next_char <- chars[next_index]
#   generated <- paste(generated, next_char, sep = "")
#   cur.sentence <- c(cur.sentence[-1], next_char)
# }
