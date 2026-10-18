(function () {
  'use strict';

  var FONT = '"Times New Roman", Tinos, "Liberation Serif", serif';
  var BLUE = '#2a78d6';
  var ORANGE = '#eb6834';
  var GREEN = '#1baf7a';
  var GREY = '#6b6a66';
  var MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var RANKING = [3, 6, 9, 12];
  var HOLDING = [3, 6, 9, 12];

  var state = { universe: 'B', ranking: 6, holding: 6, gap: 'noskip' };
  var returns = null;
  var tables = null;
  var meta = null;
  var charts = {};

  function byId(id) {
    return document.getElementById(id);
  }

  function pct(value, digits) {
    if (value === null || value === undefined || isNaN(value)) {
      return '–';
    }
    return (value * 100).toFixed(digits === undefined ? 2 : digits) + '%';
  }

  function num(value, digits) {
    if (value === null || value === undefined || isNaN(value)) {
      return '–';
    }
    return Number(value).toFixed(digits === undefined ? 2 : digits);
  }

  function universeLabel(code) {
    return code === 'A' ? 'all NSE shares' : '500 most traded';
  }

  function strategyKey() {
    return state.universe + '_' + state.gap + '_' + state.ranking + '_' + state.holding;
  }

  function rowsOf(name) {
    return tables[name];
  }

  function pickRow(name, test) {
    var rows = rowsOf(name);
    for (var index = 0; index < rows.length; index += 1) {
      if (test(rows[index])) {
        return rows[index];
      }
    }
    return null;
  }

  function filterRows(name, test) {
    return rowsOf(name).filter(test);
  }

  function seriesStats(series) {
    var values = series.filter(function (x) { return x !== null; });
    var count = values.length;
    var growth = 1;
    var peak = 1;
    var maxDrawdown = 0;
    var sum = 0;
    var positive = 0;
    var worst = Infinity;
    var best = -Infinity;
    values.forEach(function (x) {
      growth *= 1 + x;
      peak = Math.max(peak, growth);
      maxDrawdown = Math.min(maxDrawdown, growth / peak - 1);
      sum += x;
      positive += x > 0 ? 1 : 0;
      worst = Math.min(worst, x);
      best = Math.max(best, x);
    });
    var mean = sum / count;
    var variance = 0;
    values.forEach(function (x) { variance += (x - mean) * (x - mean); });
    var volatility = Math.sqrt(variance / (count - 1)) * Math.sqrt(12);
    return {
      count: count,
      cagr: Math.pow(growth, 12 / count) - 1,
      mean: mean,
      volatility: volatility,
      maxDrawdown: maxDrawdown,
      worst: worst,
      best: best,
      positive: positive / count,
      growth: growth
    };
  }

  function growthCurve(series) {
    var wealth = 1;
    return series.map(function (x) {
      wealth *= 1 + (x === null ? 0 : x);
      return wealth;
    });
  }

  function drawdownCurve(series) {
    var wealth = 1;
    var peak = 1;
    return series.map(function (x) {
      wealth *= 1 + (x === null ? 0 : x);
      peak = Math.max(peak, wealth);
      return (wealth / peak - 1) * 100;
    });
  }

  function chart(id) {
    if (!charts[id]) {
      charts[id] = echarts.init(byId(id), null, { renderer: 'svg' });
    }
    return charts[id];
  }

  function baseOption() {
    return {
      animation: false,
      textStyle: { fontFamily: FONT, fontSize: 12 },
      grid: { left: 56, right: 20, top: 40, bottom: 36 },
      legend: { top: 0, itemGap: 28, textStyle: { fontFamily: FONT } },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross', label: { fontFamily: FONT } },
        textStyle: { fontFamily: FONT }
      }
    };
  }

  function drawTable(id, header, rows, note, textColumns) {
    var textCount = textColumns || 1;
    var html = '<thead><tr>';
    header.forEach(function (label, position) {
      html += '<th class="' + (position < textCount ? 'text' : '') + '">' + label + '</th>';
    });
    html += '</tr></thead><tbody>';
    rows.forEach(function (row) {
      var classes = row.highlight ? ' class="highlight"' : '';
      html += '<tr' + classes + '>';
      row.cells.forEach(function (cell, position) {
        html += '<td class="' + (position < textCount ? 'text' : '') + '">' + cell + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody>';
    byId(id).innerHTML = html;
    var existing = byId(id).parentNode.querySelector('.table-note');
    if (existing) {
      existing.remove();
    }
    if (note) {
      var paragraph = document.createElement('p');
      paragraph.className = 'table-note';
      paragraph.innerHTML = note;
      byId(id).parentNode.appendChild(paragraph);
    }
  }

  function row(cells, highlight) {
    return { cells: cells, highlight: !!highlight };
  }

  function currentSeries() {
    return returns.strategies[strategyKey()];
  }

  function drawSummary() {
    var entry = currentSeries();
    var portfolio = seriesStats(entry.lo);
    var paperPortfolio = seriesStats(entry.ls);
    var bench = seriesStats(returns.benchmark);
    var line = pickRow('table_one', function (r) {
      return r.universe === state.universe && r.skip === (state.gap === 'skip') && r.J === state.ranking && r.K === state.holding;
    });
    byId('specification-summary').textContent =
      universeLabel(state.universe) + ', J = ' + state.ranking + ', K = ' + state.holding +
      (state.gap === 'skip' ? ', one-week gap' : ', no gap') + ': the winners decile compounded at ' +
      pct(portfolio.cagr, 1) + ' a year after costs against ' + pct(bench.cagr, 1) +
      ' for the NIFTY 500 total return; the winners-minus-losers spread earned ' + pct(line.bs_mean) +
      ' a month before costs.';
    var header = ['', 'Winners decile', 'Winners minus losers', 'NIFTY 500 total return'];
    var rows = [
      row(['Compound annual return, after costs', pct(portfolio.cagr, 1), pct(paperPortfolio.cagr, 1), pct(bench.cagr, 1)]),
      row(['Mean monthly return, after costs', pct(portfolio.mean), pct(paperPortfolio.mean), pct(bench.mean)]),
      row(['Newey–West <i>t</i>-statistic of the mean', num(line.lo_net_t_nw, 1), num(line.bs_net_t_nw, 1), '–']),
      row(['Annualised volatility', pct(portfolio.volatility, 1), pct(paperPortfolio.volatility, 1), pct(bench.volatility, 1)]),
      row(['Worst drawdown', pct(portfolio.maxDrawdown, 0), pct(paperPortfolio.maxDrawdown, 0), pct(bench.maxDrawdown, 0)]),
      row(['Worst month', pct(portfolio.worst, 1), pct(paperPortfolio.worst, 1), pct(bench.worst, 1)]),
      row(['Months with a positive return', pct(portfolio.positive, 0), pct(paperPortfolio.positive, 0), pct(bench.positive, 0)]),
      row(['Excess over the index, a year', pct(line.lo_net_excess_annual, 1), '–', '–']),
      row(['Turnover a month (bought plus sold)', num(line.lo_turnover, 2), num(line.bs_turnover, 2), '–'])
    ];
    drawTable('table-summary', header, rows,
      '<b>Table 2.</b> Selected portfolio, ' + meta.first_month + ' to ' + meta.last_month + ' (' + meta.months +
      ' months), after Indian delivery costs. The winners-minus-losers portfolio is a paper portfolio: most investors in India cannot short cash shares overnight, and no borrowing cost is charged.');
  }

  function drawGrowth() {
    var entry = currentSeries();
    var option = baseOption();
    option.xAxis = { type: 'category', data: returns.months, axisLabel: { interval: 23, fontFamily: FONT } };
    option.yAxis = { type: 'log', min: 0.5, axisLabel: { fontFamily: FONT, formatter: function (v) { return '₹' + v; } } };
    option.series = [
      { name: 'Winners decile', type: 'line', showSymbol: false, data: growthCurve(entry.lo), lineStyle: { color: BLUE, width: 2 }, itemStyle: { color: BLUE } },
      { name: 'Winners minus losers (paper portfolio)', type: 'line', showSymbol: false, data: growthCurve(entry.ls), lineStyle: { color: GREEN, width: 1.5, type: 'dashed' }, itemStyle: { color: GREEN } },
      { name: 'NIFTY 500 total return', type: 'line', showSymbol: false, data: growthCurve(returns.benchmark), lineStyle: { color: ORANGE, width: 2 }, itemStyle: { color: ORANGE } }
    ];
    chart('figure-growth').setOption(option, true);
  }

  function drawDrawdown() {
    var entry = currentSeries();
    var option = baseOption();
    option.xAxis = { type: 'category', data: returns.months, axisLabel: { interval: 23, fontFamily: FONT } };
    option.yAxis = { type: 'value', max: 0, axisLabel: { fontFamily: FONT, formatter: '{value}%' } };
    option.series = [
      { name: 'Winners decile', type: 'line', showSymbol: false, data: drawdownCurve(entry.lo), lineStyle: { color: BLUE, width: 1.5 }, itemStyle: { color: BLUE } },
      { name: 'NIFTY 500 total return', type: 'line', showSymbol: false, data: drawdownCurve(returns.benchmark), lineStyle: { color: ORANGE, width: 1.5 }, itemStyle: { color: ORANGE } }
    ];
    chart('figure-drawdown').setOption(option, true);
  }

  function drawCalendar() {
    var entry = currentSeries();
    var firstYear = parseInt(returns.months[0].slice(0, 4), 10);
    var lastYear = parseInt(returns.months[returns.months.length - 1].slice(0, 4), 10);
    var years = [];
    for (var year = firstYear; year <= lastYear; year += 1) {
      years.push(String(year));
    }
    var data = [];
    returns.months.forEach(function (month, position) {
      if (entry.lo[position] === null || returns.benchmark[position] === null) {
        return;
      }
      var yearIndex = parseInt(month.slice(0, 4), 10) - firstYear;
      var monthIndex = parseInt(month.slice(5, 7), 10) - 1;
      data.push([monthIndex, yearIndex, Math.round((entry.lo[position] - returns.benchmark[position]) * 1000) / 10]);
    });
    var option = baseOption();
    option.grid = { left: 48, right: 20, top: 16, bottom: 60 };
    option.legend = undefined;
    option.tooltip = { formatter: function (p) { return years[p.value[1]] + ' ' + MONTH_NAMES[p.value[0]] + ': ' + p.value[2].toFixed(1) + ' points'; }, textStyle: { fontFamily: FONT } };
    option.xAxis = { type: 'category', data: MONTH_NAMES, splitArea: { show: false }, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'category', data: years, inverse: true, axisLabel: { fontFamily: FONT } };
    option.visualMap = {
      min: -10, max: 10, calculable: false, orient: 'horizontal', left: 'center', bottom: 4,
      inRange: { color: ['#b3302f', '#e8908f', '#f0efec', '#86b6ef', '#1c5cab'] },
      textStyle: { fontFamily: FONT }, formatter: function (v) { return v + ' pts'; }
    };
    option.series = [{
      type: 'heatmap', data: data,
      label: { show: true, fontFamily: FONT, fontSize: 9, formatter: function (p) { return p.value[2].toFixed(0); } },
      itemStyle: { borderColor: '#fcfcfb', borderWidth: 1 }
    }];
    chart('figure-calendar').setOption(option, true);
  }

  function drawRolling() {
    var entry = currentSeries();
    var span = 36;
    var data = [];
    var labels = [];
    for (var end = span - 1; end < returns.months.length; end += 1) {
      var growthPortfolio = 1;
      var growthBenchmark = 1;
      for (var position = end - span + 1; position <= end; position += 1) {
        growthPortfolio *= 1 + (entry.lo[position] || 0);
        growthBenchmark *= 1 + (returns.benchmark[position] || 0);
      }
      data.push(Math.round((Math.pow(growthPortfolio, 12 / span) - Math.pow(growthBenchmark, 12 / span)) * 1000) / 10);
      labels.push(returns.months[end]);
    }
    var option = baseOption();
    option.legend = undefined;
    option.xAxis = { type: 'category', data: labels, axisLabel: { interval: 23, fontFamily: FONT } };
    option.yAxis = { type: 'value', axisLabel: { fontFamily: FONT, formatter: '{value} pts' } };
    option.series = [{
      type: 'line', showSymbol: false, data: data, lineStyle: { color: BLUE, width: 1.5 }, itemStyle: { color: BLUE },
      markLine: { symbol: 'none', silent: true, data: [{ yAxis: 0 }], lineStyle: { color: GREY } }
    }];
    chart('figure-rolling').setOption(option, true);
  }

  function paperCell(panel, ranking, holding) {
    var found = pickRow('paper_table_i', function (r) {
      return r.panel === panel && r.leg === 'buy_sell' && r.J === ranking && r.K === holding;
    });
    return found;
  }

  function drawTableOne() {
    var skip = state.gap === 'skip';
    var panel = skip ? 'B' : 'A';
    var header = ['<i>J</i>', '<i>K</i> = 3', '<i>K</i> = 6', '<i>K</i> = 9', '<i>K</i> = 12'];
    var grossRows = [];
    var netRows = [];
    RANKING.forEach(function (ranking) {
      var grossCells = ['<i>J</i> = ' + ranking];
      var netCells = ['<i>J</i> = ' + ranking];
      HOLDING.forEach(function (holding) {
        var line = pickRow('table_one', function (r) {
          return r.universe === state.universe && r.skip === skip && r.J === ranking && r.K === holding;
        });
        var paper = paperCell(panel, ranking, holding);
        grossCells.push(pct(line.bs_mean) + ' (' + num(line.bs_t_ols, 1) + ')<br><span class="muted">paper ' + pct(paper.mean_monthly_return) + ' (' + num(paper.t_statistic, 2) + ')</span>');
        netCells.push(pct(line.bs_net_mean) + ' (' + num(line.bs_net_t_nw, 1) + ')');
      });
      var selected = ranking === state.ranking;
      grossRows.push({ cells: grossCells, highlight: selected });
      netRows.push({ cells: netCells, highlight: selected });
    });
    drawTable('table-one', header, grossRows,
      '<b>Table 1.</b> Buy-minus-sell return per month before costs, ' + universeLabel(state.universe) + (skip ? ', one-week gap' : ', no gap') +
      '; ordinary <i>t</i>-statistics in brackets, with the paper\'s values (1965–1989, NYSE and AMEX) beneath. The shaded row is the selected ranking period <i>J</i> = ' + state.ranking + '.');
    drawTable('table-one-net', header, netRows,
      '<b>Table 1b.</b> The same strategies after Indian delivery costs, with Newey–West <i>t</i>-statistics in brackets. The long-short portfolio is charged the same costs on both legs.');
  }

  function drawHeatmap() {
    var skip = state.gap === 'skip';
    var data = [];
    RANKING.forEach(function (ranking, rowIndex) {
      HOLDING.forEach(function (holding, columnIndex) {
        var line = pickRow('table_one', function (r) {
          return r.universe === state.universe && r.skip === skip && r.J === ranking && r.K === holding;
        });
        data.push([columnIndex, rowIndex, Math.round(line.lo_net_excess_annual * 1000) / 10]);
      });
    });
    var option = baseOption();
    option.legend = undefined;
    option.grid = { left: 60, right: 16, top: 16, bottom: 56 };
    option.tooltip = { formatter: function (p) { return 'J = ' + RANKING[p.value[1]] + ', K = ' + HOLDING[p.value[0]] + ': ' + p.value[2].toFixed(1) + ' points a year'; }, textStyle: { fontFamily: FONT } };
    option.xAxis = { type: 'category', data: HOLDING.map(function (x) { return 'K = ' + x; }), axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'category', data: RANKING.map(function (x) { return 'J = ' + x; }), inverse: true, axisLabel: { fontFamily: FONT } };
    option.visualMap = { min: 0, max: 12, calculable: false, orient: 'horizontal', left: 'center', bottom: 4, inRange: { color: ['#f0efec', '#86b6ef', '#1c5cab'] }, textStyle: { fontFamily: FONT } };
    option.series = [{
      type: 'heatmap', data: data,
      label: { show: true, fontFamily: FONT, formatter: function (p) { return p.value[2].toFixed(1); } },
      itemStyle: { borderColor: '#fcfcfb', borderWidth: 2 }
    }];
    chart('figure-heatmap').setOption(option, true);
  }

  function drawScatter() {
    var bySet = { A: [], B: [] };
    var selected = null;
    rowsOf('table_one').forEach(function (r) {
      var point = {
        value: [Math.abs(r.lo_net_max_drawdown) * 100, r.lo_net_cagr * 100],
        label: r.universe + ' J' + r.J + '/K' + r.K + (r.skip ? ' gap' : '')
      };
      bySet[r.universe].push(point);
      if (r.universe === state.universe && r.skip === (state.gap === 'skip') && r.J === state.ranking && r.K === state.holding) {
        selected = point;
      }
    });
    var option = baseOption();
    option.grid = { left: 60, right: 16, top: 40, bottom: 44 };
    option.tooltip = { trigger: 'item', formatter: function (p) { return p.data.label + '<br>' + p.data.value[1].toFixed(1) + '% a year, worst fall ' + p.data.value[0].toFixed(0) + '%'; }, textStyle: { fontFamily: FONT } };
    option.xAxis = { type: 'value', name: 'Worst drawdown, %', nameLocation: 'middle', nameGap: 26, min: 55, max: 80, nameTextStyle: { fontFamily: FONT }, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', name: 'Compound annual return, %', nameLocation: 'middle', nameGap: 38, nameTextStyle: { fontFamily: FONT }, axisLabel: { fontFamily: FONT } };
    option.series = [
      { name: 'All shares', type: 'scatter', data: bySet.A, symbolSize: 8, itemStyle: { color: ORANGE, opacity: 0.75 } },
      { name: '500 most traded', type: 'scatter', data: bySet.B, symbolSize: 8, itemStyle: { color: BLUE, opacity: 0.75 } },
      { name: 'Selected', type: 'scatter', data: selected ? [selected] : [], symbolSize: 18, itemStyle: { color: 'rgba(0,0,0,0)', borderColor: '#0b0b0b', borderWidth: 2 }, silent: true, tooltip: { show: false } }
    ];
    chart('figure-scatter').setOption(option, true);
  }

  function drawSkipNote() {
    var universe = state.universe;
    var sum = { none: 0, main: 0 };
    rowsOf('table_one').forEach(function (r) {
      if (r.universe !== universe) {
        return;
      }
      sum[r.skip ? 'main' : 'none'] += r.bs_mean / 16;
    });
    var early = 0;
    rowsOf('table_one_earlier_ranking_skip').forEach(function (r) {
      if (r.universe === universe) {
        early += r.mean / 16;
      }
    });
    byId('skip-note').innerHTML = '<b>The skipped week.</b> For ' + universeLabel(universe) + ', the 16 spreads average ' + pct(sum.none, 2) +
      ' a month with no gap, ' + pct(sum.main, 2) + ' when holding starts a week after a month-end ranking (the gap used here), and ' + pct(early, 2) +
      ' when the ranking window instead ends a week before the month end. The paper\'s finding that a gap raises returns therefore holds in India or not depending on where in the calendar month the week falls.';
  }

  function drawBeta() {
    var india = [];
    var rows = filterRows('table_two', function (r) { return r.universe === state.universe; });
    for (var decile = 1; decile <= 10; decile += 1) {
      var found = rows.filter(function (r) { return String(r.portfolio) === String(decile); })[0];
      india.push(Math.round(found.beta * 100) / 100);
    }
    var option = baseOption();
    option.xAxis = { type: 'category', data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], name: 'Past-return decile', nameLocation: 'middle', nameGap: 26, nameTextStyle: { fontFamily: FONT }, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', min: 0, axisLabel: { fontFamily: FONT } };
    option.series = [
      { name: 'India, ' + universeLabel(state.universe), type: 'bar', data: india, itemStyle: { color: BLUE } },
      { name: 'Paper', type: 'bar', data: tables.paper_numbers.table_ii_beta, itemStyle: { color: ORANGE } }
    ];
    chart('figure-beta').setOption(option, true);
    var spread = rows.filter(function (r) { return r.portfolio === 'P10-P1'; })[0];
    var size1 = rows.filter(function (r) { return String(r.portfolio) === '1'; })[0];
    var size10 = rows.filter(function (r) { return String(r.portfolio) === '10'; })[0];
    drawTable('table-beta', ['', 'Losers (decile 1)', 'Winners (decile 10)', 'Winners minus losers'], [
      row(['Beta, India (' + universeLabel(state.universe) + ')', num(size1.beta), num(size10.beta), num(spread.beta)]),
      row(['Beta, paper', '1.36', '1.28', '–0.08']),
      row(['Median daily traded value, ₹ crore', num(size1.median_traded_value_crore, 1), num(size10.median_traded_value_crore, 1), '–'])
    ], '<b>Table 3.</b> Betas of the six-month/six-month deciles. India has no free market-capitalisation history before February 2024, so size is the median daily traded value in ₹ crore.');
  }

  function drawSubsamples() {
    var names = ['All', 'S1', 'S2', 'S3', 'B1', 'B2', 'B3'];
    var cells = ['India, raw'];
    var alphaCells = ['India, alpha'];
    names.forEach(function (name) {
      var found = pickRow('table_three', function (r) {
        return r.universe === state.universe && r.subsample === name && r.portfolio === 'P10-P1';
      });
      cells.push(pct(found.mean) + ' (' + num(found.t, 1) + ')');
      alphaCells.push(pct(found.alpha) + ' (' + num(found.alpha_t, 1) + ')');
    });
    var paperCells = ['Paper, raw'];
    names.forEach(function (name) {
      paperCells.push(pct(tables.paper_numbers.table_iii_all_p10_p1[name]));
    });
    drawTable('table-subsamples', ['6/6 spread', 'All', 'Small', 'Medium', 'Large', 'Low beta', 'Mid beta', 'High beta'],
      [row(cells), row(alphaCells), row(paperCells)],
      '<b>Table 4.</b> Winners minus losers within size thirds (by median daily traded value) and beta thirds (Scholes–Williams betas of the previous calendar year), ' + universeLabel(state.universe) +
      '. Alphas are against the NIFTY 500 total return in excess of the Treasury bill return, to December 2025; <i>t</i>-statistics in brackets.');
  }

  function drawCalendarMonths() {
    var india = MONTH_NAMES.map(function (name) {
      var found = pickRow('table_four_five', function (r) {
        return r.universe === state.universe && r.subsample === 'All' && r.months === name;
      });
      return Math.round(found.mean * 1000) / 10;
    });
    var paper = MONTH_NAMES.map(function (name) {
      return Math.round(tables.paper_numbers.table_iv[name] * 1000) / 10;
    });
    var option = baseOption();
    option.xAxis = { type: 'category', data: MONTH_NAMES, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', axisLabel: { fontFamily: FONT, formatter: '{value}%' } };
    option.series = [
      { name: 'India, ' + universeLabel(state.universe), type: 'bar', data: india, itemStyle: { color: BLUE } },
      { name: 'Paper', type: 'bar', data: paper, itemStyle: { color: ORANGE } }
    ];
    chart('figure-calendar-months').setOption(option, true);
  }

  function drawSubperiods() {
    var periods = ['2007-2011', '2012-2016', '2017-2021', '2022-2026'];
    var rowsOut = [];
    ['All', 'All except Mar'].forEach(function (months) {
      var cells = [months === 'All' ? 'All months' : 'All months except March'];
      periods.forEach(function (period) {
        var found = pickRow('table_six', function (r) {
          return r.universe === state.universe && r.subsample === 'All' && r.months === months && r.subperiod === period;
        });
        cells.push(pct(found.mean) + ' (' + num(found.t, 1) + ')');
      });
      rowsOut.push(row(cells));
    });
    drawTable('table-subperiods', ['6/6 spread', '2007–11', '2012–16', '2017–21', '2022–Sep 26'], rowsOut,
      '<b>Table 5.</b> Average monthly winners-minus-losers return by subperiod before costs, ' + universeLabel(state.universe) +
      '; ordinary <i>t</i>-statistics in brackets. The paper\'s five-year subperiods, 1965–89: 1.23%, 1.09%, –0.44%, 1.27%, 1.62%.');
  }

  function drawEvent() {
    function cumulative(name) {
      return filterRows(name, function (r) { return r.universe === state.universe; }).map(function (r) {
        return Math.round(r.cumulative * 1000) / 10;
      });
    }
    var months = [];
    for (var month = 1; month <= 36; month += 1) {
      months.push(month);
    }
    var option = baseOption();
    option.xAxis = { type: 'category', data: months, name: 'Months after ranking', nameLocation: 'middle', nameGap: 26, nameTextStyle: { fontFamily: FONT }, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', axisLabel: { fontFamily: FONT, formatter: '{value}%' } };
    option.series = [
      { name: 'India 2007–2026', type: 'line', showSymbol: false, data: cumulative('table_seven'), lineStyle: { color: BLUE, width: 2 }, itemStyle: { color: BLUE } },
      { name: 'India 1997–2006 (early sample)', type: 'line', showSymbol: false, data: cumulative('table_eight_early_sample'), lineStyle: { color: GREEN, width: 2 }, itemStyle: { color: GREEN } },
      { name: 'Paper 1965–1989', type: 'line', showSymbol: false, data: tables.paper_numbers.table_vii_cumulative_all.map(function (x) { return Math.round(x * 1000) / 10; }), lineStyle: { color: ORANGE, width: 2 }, itemStyle: { color: ORANGE } }
    ];
    chart('figure-event').setOption(option, true);
  }

  function drawSectionThree() {
    var quantities = Object.keys(tables.paper_numbers.section_iii);
    var labels = {
      'WRSS profit per dollar long per half-year': 'Weighted strategy profit per dollar long, per half-year',
      'serial covariance of half-year equal-weight index': 'Serial covariance of six-month equal-weight index returns',
      'average serial covariance of residuals': 'Average serial covariance of market-model residuals',
      'lead-lag theta, all': 'Lead–lag regression coefficient on the squared past market return'
    };
    var rowsOut = quantities.map(function (quantity) {
      var found = pickRow('section_three', function (r) { return r.universe === state.universe && r.quantity === quantity; });
      var value = num(found.value, 4);
      if (found.t !== null) {
        value += ' (' + num(found.t, 2) + ')';
      }
      return row([labels[quantity] || quantity, value, num(tables.paper_numbers.section_iii[quantity], 4)]);
    });
    drawTable('table-section-three', ['', 'India, ' + universeLabel(state.universe), 'Paper'], rowsOut,
      '<b>Table 6.</b> The weighted relative strength strategy (profit per dollar long over six months), the serial covariance of six-month returns of an equally weighted index and of market-model residuals, and the regression of six-month profits on the squared past market return (a negative coefficient is inconsistent with a lead–lag explanation). <i>t</i>-statistics in brackets.');
  }

  function drawEarnings() {
    var india = filterRows('table_nine', function (r) { return r.universe === state.universe; }).map(function (r) {
      return Math.round(r.winners_minus_losers * 10000) / 100;
    });
    var months = [];
    for (var month = 1; month <= 36; month += 1) {
      months.push(month);
    }
    var option = baseOption();
    option.xAxis = { type: 'category', data: months, name: 'Months after ranking', nameLocation: 'middle', nameGap: 26, nameTextStyle: { fontFamily: FONT }, axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', axisLabel: { fontFamily: FONT, formatter: '{value}%' } };
    option.series = [
      { name: 'India, ' + universeLabel(state.universe), type: 'bar', data: india, itemStyle: { color: BLUE } },
      { name: 'Paper', type: 'line', showSymbol: false, data: tables.paper_numbers.table_ix_all.map(function (x) { return Math.round(x * 10000) / 100; }), lineStyle: { color: ORANGE, width: 2 }, itemStyle: { color: ORANGE } }
    ];
    chart('figure-earnings').setOption(option, true);
  }

  function drawHeadlineTables() {
    var headerOne = ['Universe', 'Portfolio', 'Impact per side', 'Gross mean', 'Net mean', 'NW <i>t</i>', 'CAGR', 'Worst fall', 'Turnover'];
    var rowsOne = rowsOf('headline_strategies').map(function (r) {
      return row([
        r.universe, r.strategy, pct(r.impact_cost, 1), pct(r.gross_mean), pct(r.net_mean), num(r.net_t_nw, 1), pct(r.net_cagr, 1), pct(r.max_drawdown, 0), num(r.turnover, 2)
      ], (r.universe === 'B' && r.impact_cost === 0.001));
    });
    drawTable('table-headline', headerOne, rowsOne,
      '<b>Table 7.</b> The headline six-month/six-month strategy without a gap at several levels of assumed market impact. The assumed impact is 0.3% a side for all shares and 0.1% for the 500 most traded (shaded: universe B). The NIFTY 500 total return compounded at ' + pct(meta.benchmark_cagr, 1) + ' a year.', 2);
    var variants = [];
    rowsOf('robustness').forEach(function (r) {
      if (variants.indexOf(r.variant) < 0) {
        variants.push(r.variant);
      }
    });
    var rowsTwo = variants.map(function (variant) {
      var cells = [variant];
      ['A', 'B'].forEach(function (universe) {
        ['gross', 'net', 'net at double impact'].forEach(function (kind) {
          var found = pickRow('robustness', function (r) { return r.universe === universe && r.variant === variant && r.return === kind; });
          cells.push(pct(found.mean) + (kind === 'gross' ? ' (' + num(found.t_nw, 1) + ')' : ''));
        });
      });
      return row(cells);
    });
    drawTable('table-robustness', ['6/6 spread', 'A gross (NW <i>t</i>)', 'A net', 'A net, 2× impact', 'B gross (NW <i>t</i>)', 'B net', 'B net, 2× impact'], rowsTwo,
      '<b>Table 8.</b> Robustness of the six-month/six-month winners-minus-losers spread: leaving out 2009, March or January, dropping shares that ever gained more than 300% in a month, and winsorising monthly returns at +100%.');
    var treatments = ['none', 'both legs', 'losers only', 'winners only'];
    var rowsThree = treatments.map(function (treatment) {
      var cells = [treatment];
      ['A', 'B'].forEach(function (universe) {
        var found = pickRow('delisting_stress', function (r) { return r.universe === universe && r.treatment === treatment; });
        cells.push(pct(found.mean) + ' (' + num(found.t_nw, 1) + ')');
      });
      return row(cells);
    });
    drawTable('table-delisting', ['Exit loss of 100% charged to', 'All shares', '500 most traded'], rowsThree,
      '<b>Table 9.</b> Delisting stress. Nothing is charged after a share\'s last trade in the main results. This table charges a 100% loss in the month after the last return of every share that disappears for good, an extreme bound because many exits are mergers or symbol changes. Mean monthly spread before costs, Newey–West <i>t</i>-statistics in brackets.');
  }

  function drawWealth() {
    var rows = rowsOf('wealth_by_year');
    var option = baseOption();
    option.legend = undefined;
    option.xAxis = { type: 'category', data: rows.map(function (r) { return String(r.year); }), axisLabel: { fontFamily: FONT } };
    option.yAxis = { type: 'value', axisLabel: { fontFamily: FONT } };
    option.series = [{
      type: 'bar',
      data: rows.map(function (r) { return Math.round(r.winners_long_only / r.nifty500_tri * 100) / 100; }),
      itemStyle: { color: BLUE },
      markLine: { symbol: 'none', silent: true, data: [{ yAxis: 1 }], lineStyle: { color: GREY } }
    }];
    chart('figure-wealth').setOption(option, true);
  }

  function renderAll() {
    drawSummary();
    drawGrowth();
    drawDrawdown();
    drawCalendar();
    drawRolling();
    drawTableOne();
    drawHeatmap();
    drawScatter();
    drawSkipNote();
    drawBeta();
    drawSubsamples();
    drawCalendarMonths();
    drawSubperiods();
    drawEvent();
    drawSectionThree();
    drawEarnings();
    drawHeadlineTables();
    drawWealth();
  }

  function hashFor() {
    return '#' + state.universe.toLowerCase() + '-j' + state.ranking + '-k' + state.holding + '-' + state.gap;
  }

  function readHash() {
    var match = /^#([ab])-j(\d+)-k(\d+)-(noskip|skip)$/i.exec(window.location.hash);
    if (!match) {
      return;
    }
    var ranking = parseInt(match[2], 10);
    var holding = parseInt(match[3], 10);
    if (RANKING.indexOf(ranking) < 0 || HOLDING.indexOf(holding) < 0) {
      return;
    }
    state.universe = match[1].toUpperCase();
    state.ranking = ranking;
    state.holding = holding;
    state.gap = match[4].toLowerCase();
  }

  function syncControls() {
    byId('control-ranking').value = String(state.ranking);
    byId('control-holding').value = String(state.holding);
    byId('control-gap').value = state.gap;
    byId('control-universe').value = state.universe;
  }

  function onChange() {
    state.ranking = parseInt(byId('control-ranking').value, 10);
    state.holding = parseInt(byId('control-holding').value, 10);
    state.gap = byId('control-gap').value;
    state.universe = byId('control-universe').value;
    history.replaceState(null, '', hashFor());
    renderAll();
  }

  function fillControls() {
    RANKING.forEach(function (value) {
      var option = document.createElement('option');
      option.value = String(value);
      option.textContent = value + ' months';
      byId('control-ranking').appendChild(option);
    });
    HOLDING.forEach(function (value) {
      var option = document.createElement('option');
      option.value = String(value);
      option.textContent = value + ' months';
      byId('control-holding').appendChild(option);
    });
    ['control-ranking', 'control-holding', 'control-gap', 'control-universe'].forEach(function (id) {
      byId(id).addEventListener('change', onChange);
    });
  }

  function fillStaticNumbers() {
    byId('data-through').textContent = meta.last_month;
    byId('generated').textContent = meta.generated;
    byId('abstract-return').textContent = pct(meta.headline_cagr, 1);
    byId('abstract-benchmark').textContent = pct(meta.benchmark_cagr, 1);
    byId('abstract-drawdown').textContent = pct(Math.abs(meta.headline_drawdown), 0);
    byId('copy-citation').addEventListener('click', function () {
      var text = byId('citation-text').textContent;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
      }
      byId('copy-citation').textContent = 'Copied';
      setTimeout(function () { byId('copy-citation').textContent = 'Copy'; }, 1500);
    });
  }

  function start() {
    Promise.all([
      fetch('data/returns.json').then(function (r) { return r.json(); }),
      fetch('data/tables.json').then(function (r) { return r.json(); }),
      fetch('data/meta.json').then(function (r) { return r.json(); })
    ]).then(function (loaded) {
      returns = loaded[0];
      tables = loaded[1];
      meta = loaded[2];
      fillControls();
      readHash();
      syncControls();
      fillStaticNumbers();
      renderAll();
      window.addEventListener('hashchange', function () { readHash(); syncControls(); renderAll(); });
      window.addEventListener('resize', function () {
        Object.keys(charts).forEach(function (id) { charts[id].resize(); });
      });
    }).catch(function (error) {
      byId('specification-summary').textContent = 'The data files could not be loaded: ' + error;
    });
  }

  start();
}());
