library(keras)
library(dplyr)
library(purrr)

setwd('/home/aw/Documents/w/py/scrape-recipes')
f.names = list.files(pattern = '*.txt')

cleanChars = function(txt) {
  txt = gsub('[\']|[‘]|[’]|[“]|[”]|[″]|["]|[\u2028]|[­]|[🙂]|[~]|[=]|[>]', '', txt)
  txt = gsub('\024', '', txt)
  txt = gsub('[–]|[—]|[̶]', '-', txt)
  txt = gsub('[º]|[°]|[˚]', '⁰', txt)
  txt = gsub('[⁄]', '/', txt)
  txt = gsub('[[]|[{]', '(', txt)
  txt = gsub('[]]|[}]', '(', txt)
  txt = gsub('[¢]|[£]', '$', txt)
  txt = gsub('\t', ' ', txt)
  txt = gsub('[×]', 'x', txt)
  txt = gsub('[⅙]', '1/6', txt)
  txt = gsub('[⅜]', '3/8', txt)
  txt = gsub('[⅔]', '2/3', txt)
  txt = gsub('[⅝]', '5/8', txt)
  txt = gsub('[⅓]', '1/3', txt)
  txt = gsub('[⅛]', '1/8', txt)
  txt = gsub('[¾]', '3/4', txt)
  txt = gsub('[¼]', '1/4', txt)
  txt = gsub('[½]', '1/2', txt)
  txt = gsub('[à]|[â]|[å]|[ä]', 'a', txt)
  txt = gsub('[ç]', 'c', txt)
  txt = gsub('[é]|[è]|[ê]|[ë]', 'e', txt)
  txt = gsub('[í]|[î]|[ï]', 'i', txt)
  txt = gsub('[ó]|[ô]|[ö]', 'o', txt)
  txt = gsub('[ú]|[ù]|[û]', 'u', txt)
  txt = gsub('[ﬂ]|[ﬁ]', 'fl', txt)
  txt = txt[!grepl('[<]', txt)] # line of html
  txt = gsub('#', 'number ', txt)
  txt = gsub('[|]', 'or', txt)
  txt
}

all.recipes = list()
all.sentences = character()
all.titles = character()
print('reading in txt files...')
for (f.name in f.names[2000:7540]) {
  f.lines = readLines(f.name, warn = F)
  if (f.lines[1] %in% all.titles) next
  all.titles = c(all.titles, f.lines[1])
  methodIdx = which(f.lines == '==========')[2] + 1
  methodLines = f.lines[methodIdx:length(f.lines)]
  sentences = methodLines %>%
    strsplit("[.][ ]|[!][ ]") %>%
    unlist() %>%
    trimws()
  sentences = sentences[sentences != '' & nchar(sentences) > 1]
  sent.clean = tolower(paste(sub("[.]$|[!]$", "", sentences), '.', sep=''))
  sent.clean = cleanChars(sent.clean)
  sent.clean = sent.clean[sent.clean != '']
  all.sentences = c(all.sentences, sent.clean)
  all.recipes = c(all.recipes, list(sent.clean))
}
print('building data structure...')


text.block = all.sentences %>%
  paste(collapse=' ') %>%
  strsplit('') %>%
  unlist()

chars <- text.block %>%
  unique() %>%
  sort()


maxlen = 40
dataset <- map(seq(1, length(text.block) - maxlen - 1, by = 1),
          ~list(sentence = paste(text.block[.x:(.x + maxlen - 1)], collapse=''), next_char = text.block[.x + maxlen])) %>%
  transpose()
all.x.y = data.frame(x=unlist(dataset[[1]]), y=unlist(dataset[[2]]))
num.data = nrow(all.x.y)


data_generator <- function(data, batch_size) {
  i <- 1
  function() {
    # reset iterator if already seen all data
    if ((i + batch_size - 1) > nrow(data)) i <<- 1
    # iterate current batch's rows
    row.indeces <- c(i:min(i + batch_size - 1, nrow(data)))
    
    x <- array(0, dim = c(length(row.indeces), maxlen, length(chars)))
    y <- array(0, dim = c(length(row.indeces), length(chars)))

    for(each.row in 1:length(row.indeces)){
      pre.chars = unlist(strsplit(data$x[[i + each.row - 1]], ''))
      x[each.row,,] <- sapply(chars, function(rec.char) as.integer(rec.char == pre.chars))
      y[each.row,] <- as.integer(chars == data$y[[i + each.row - 1]])
    }
    
    # update to next iteration
    i <<- i + batch_size

    # return the batch
    list(x, y)
  }
}

gen <- data_generator(data=all.x.y, batch_size = 768)
 
optimizer <-  optimizer_rmsprop()

model <- keras_model_sequential() %>%
  layer_lstm(768, input_shape = c(maxlen, length(chars))) %>%
  layer_dense(length(chars)) %>%
  layer_dense(length(chars)) %>%
  layer_dense(length(chars)) %>%
  layer_dense(length(chars)) %>%
  layer_activation("softmax") %>%
  compile(loss = "categorical_crossentropy", optimizer = optimizer)

num.epochs = 3
model.history = model %>%
  fit_generator(gen, steps_per_epoch = num.data / 768, epochs=num.epochs)
# model = load_model_hdf5('rec3_2000_7540.model')

model.store = 'rec3_2000_7540_variable.model'
# print(paste('saving to', model.store))
# save_model_hdf5(model, model.store)

runPrediction = function() {
  start.idx <- sample(1:(length(text.block) - maxlen), size = 1)
  cur.sentence <- text.block[start.idx:(start.idx + maxlen - 1)]
  first.sentence <- cur.sentence
  generated = ''
  gen.length = 250000
  start.cat = FALSE
  cur_char = ''
  i = 1
  pb = txtProgressBar(min = i, max = gen.length, initial = 1, style = 3)
  while (i < gen.length | cur_char != '.') {
    setTxtProgressBar(pb,i)
    x.pred <- sapply(chars, function(x) as.integer(x == cur.sentence))
    x.pred <- array_reshape(x.pred, c(1, dim(x.pred)))
    
    preds <- predict(model, x.pred)
    cur_char <- sample(chars, 1, prob=preds^1.5/sum(preds^1.5))
    # cur_char <- chars[next_index]
    cur.sentence <- c(cur.sentence[-1], cur_char)
    if (start.cat) {
      generated <- paste(generated, cur_char, sep = "")
      # cat(cur_char)
    }
    if (cur_char == '.') start.cat = TRUE
    i = i + 1
  }
  close(pb)
  # cat('\n')
  pred.steps = unlist(strsplit(substring(paste(generated, ' ', sep=''), 2), '\\. '))
  cap.steps = paste(toupper(substring(pred.steps, 1, 1)),
                          substring(pred.steps, 2),
                          '.',
                          sep = "")
  cap.steps
}
pred.output = runPrediction()
pred.output
# fileConn<-file(paste('../generated_', model.store, '.txt', sep=''))
# writeLines(pred.output, fileConn)
# close(fileConn)
