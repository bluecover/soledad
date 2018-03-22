/**
 * validate v1.0.0 - light weight form validator
 * https://github.com/beiyuu/validate
 *
 * Copyright 2014, BeiYuu - http://beiyuu.com
 * Released under the MIT license - http://opensource.org/licenses/MIT
 */

!(function($, window) {
  'use strict';

  var defalut_rules = {
    require: {
      test: function(val) {
        return !val;
      },
      msg: '这是必填项，请您填写'
    },
    radioRequire: {
      test: function(val) {
        return !val;
      },
      msg: '这是必选项，请您选择'
    },
    nature: {
      test: function(val) {
        var reg_int = /^\d*$/;
        return !reg_int.test(val);
      },
      msg: '请输入正整数'
    },
    email: {
      test: function(val) {
        var r = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if(!val || r.test(val)) {
          return false;
        }
        return true;
      },
      msg: '请输入正确的邮件地址'
    },
    phone: {
      test: function(val) {
        var phone_reg = /^1[3|4|5|8|7]\d{9}$/;
        if(!val || phone_reg.test(val)) {
          return false;
        }
        return true;
      },
      msg: '请输入正确的手机号'
    }
  }

  var default_config = {
    validate_class: '.validate',
    failCallback: null,
    errorHandler: function(is_error, ele, msg) { },
    optionHandler: function(is_show, ele, msg) { },
  }

  function getEleVal(ele) {
    var val = '';
    var is_radio = $(ele).attr('type')=='radio' ? true : false;

    if(is_radio) {
      var ele_name = $(ele).attr('name')
      val = $('input[name='+ele_name+']:checked').val();
    } else {
      val = $(ele).val();
    }

    return val;
  }

  function ValidateForm(ele, rules, config) {
    if(!ele) { return; }

    this.init(ele, rules, config);
  }

  ValidateForm.prototype.init = function(ele, rules, config) {
    var node = this.node = $(ele);
    this.form = (node[0].tagName.toLowerCase() === 'form') ? node : node.find('form');
    this.rules = $.extend({}, defalut_rules, rules);
    this.config = $.extend({}, default_config, config);

    this.bindEvent();
  }

  ValidateForm.prototype.bindEvent = function() {
    this.form
      .submit($.proxy(function(e) {
        e.preventDefault()
        this.validate();
      }, this));

    this.bindFocus();
    this.bindBlur();
    this.bindKeyup();
  }

  ValidateForm.prototype.bindFocus = function() {
    var that = this;
    this.node.on('focus', this.config.validate_class, function(e) {
      var item = $(this);
      var msg = item.attr('data-validate-msg') || '';
      if(msg) {
        that.config.optionHandler(item, msg);
      }
    })
  }

  ValidateForm.prototype.bindBlur = function() {
    var that = this;
    this.node.on('blur', this.config.validate_class, function(e) {
      that.checkBlur($(this))
    })
  }

  ValidateForm.prototype.bindKeyup = function() {
    var that = this;
    this.node.on('keyup', this.config.validate_class, function(e) {
      that.checkKeyup($(this))
    })
  }

  ValidateForm.prototype.checkCondition = function(ele) {
    var condition = $(ele).attr('data-validate-condition');
    if(condition) {
      var condition_ele = $('*[name='+condition+']');
      var val = getEleVal(condition_ele);
      return val;
    }
    return true;
  }

  ValidateForm.prototype.check = function(ele, events) {
    var that = this;
    var error = '';
    var val = getEleVal(ele)

    $.each(events, function(index, item) {
      if(error) { return; }

      var rule = that.rules[item];
      if(!rule) {return}
      if(rule.test(val, ele)) {
        error = rule['msg'];
      }
    });

    if(error) {
      that.config.errorHandler(true, ele, error);
      $(ele).addClass('has-error');
    } else {
      that.config.errorHandler(false, ele);
      $(ele).removeClass('has-error');
    }
  }

  ValidateForm.prototype.checkBlur = function(ele) {
    var that = this;
    if(!this.checkCondition(ele)) {
      that.config.errorHandler(false, ele);
      $(ele).removeClass('has-error');
      return
    }

    var events = (ele.attr('data-validate')||'') + ',' + (ele.attr('data-validate-keyup')||'');
    events = events.split(',');
    if(events.length==0) {
      return;
    }
    this.check(ele, events)
  }

  ValidateForm.prototype.checkKeyup = function(ele) {
    var that = this;
    if(!this.checkCondition(ele)) {
      that.config.errorHandler(false, ele);
      $(ele).removeClass('has-error');
      return
    }

    var events = ele.attr('data-validate-keyup');
    if(!events) { return; }

    this.check(ele, events.split(','))
  }

  ValidateForm.prototype.validate = function() {
    var valis = $(this.config.validate_class, this.form);
    var that = this;
    $.each(valis, function(index, item) {
      that.checkBlur($(item));
    });
    this.handleFormSubmit()
    return !$('.has-error', this.form).length
  }

  ValidateForm.prototype.handleFormSubmit = function() {
    if($('.has-error', this.form).length) {
      this.config.failCallback(this.form)
    } else {
      if(this.config.successCallback) {
        this.config.successCallback(this.form)
      } else {
        this.form[0].submit()
      }
    }
  }

  $.fn.validateForm = function(rules, config) {
    this.each(function(index, item) {
      var vali = new ValidateForm(item, rules, config);
      $(item).data('validate', vali)
    });
    return this;
  }
})(jQuery, this);
