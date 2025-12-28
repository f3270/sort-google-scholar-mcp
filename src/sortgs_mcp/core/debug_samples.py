"""Debug HTML samples to avoid live network/archived fetches."""

DEBUG_SAMPLE_HTML = b"""
<html>
  <body>
    <div class="gs_or">
      <h3 class="gs_rt"><a href="https://example.com/paper1">Transformers for NLP</a></h3>
      <div class="gs_a">A Vaswani, N Shazeer - Advances in NLP, 2017 - example.com</div>
      <div class="gs_rs">A seminal introduction to transformer models for sequence transduction.</div>
      <div class="gs_fl">Cited by 123</div>
      <div class="gs_ggs gs_fl"><a href="https://example.com/paper1.pdf">PDF</a></div>
    </div>
    <div class="gs_or">
      <h3 class="gs_rt"><a href="https://example.com/paper2">Scaling Transformers</a></h3>
      <div class="gs_a">T Brown, B Mann - Journal of Large Models, 2020 - example.org</div>
      <div class="gs_rs">Explores large-scale transformer training and performance.</div>
      <div class="gs_fl">Cited by 456</div>
      <div class="gs_ggs gs_fl"><a href="https://example.com/paper2.pdf">PDF</a></div>
    </div>
    <div class="gs_or">
      <h3 class="gs_rt"><a href="https://example.com/paper3">Efficient Attention</a></h3>
      <div class="gs_a">N Kitaev, L Kaiser - Conference on Efficient AI, 2019 - example.net</div>
      <div class="gs_rs">Introduces sparse attention patterns to reduce compute costs.</div>
      <div class="gs_fl">Cited by 321</div>
      <div class="gs_ggs gs_fl"><a href="https://example.com/paper3.pdf">PDF</a></div>
    </div>
  </body>
</html>
"""
