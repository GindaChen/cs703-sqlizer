# Some startup commands. Don't run it as a shell file!

# Start the Sempre as a server with the grammar file
./run @mode=simple -Grammar.inPaths sqlizer/grammars/find-paper.grammar -languageAnalyzer corenlp.CoreNLPAnalyzer -Grammar.tags compositional join bridge inject -interactive false -server true

# Start a Freebase server to query over grammar
./run \
@mode=simple-freebase-nocache \
@sparqlserver=localhost:3001 \
-languageAnalyzer corenlp.CoreNLPAnalyzer \
-Grammar.inPaths sqlizer/simple.grammar \
-SimpleLexicon.inPaths sqlizer/simple.lexicon

# Start up with Freebase tutorial 
./run \
@mode=simple-freebase-nocache \
@sparqlserver=localhost:3001 \
-languageAnalyzer corenlp.CoreNLPAnalyzer \
-Grammar.inPaths freebase/data/tutorial-freebase.grammar \
-SimpleLexicon.inPaths sqlizer/tutorial-freebase.lexicon


# 
./run \
@mode=simple-freebase-nocache \
@sparqlserver=localhost:3001 \
-languageAnalyzer corenlp.CoreNLPAnalyzer \
-Grammar.inPaths sqlizer/simple.grammar \
-SimpleLexicon.inPaths sqlizer/simple.lexicon


# Execute the simple freebase sparql executor
./run @mode=simple -Executor freebase.SparqlExecutor

