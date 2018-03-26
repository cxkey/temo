
$(document).ready(function(e) {

    var pay = function(price, istype) {
        var pay_result = "#user_info span[name=pay_result]"
        $.ajax({  
            type: "post",  
            url: "/sys/pay",
            data: {'price': price, 'istype': istype},
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend: function() { 
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $("#formpay input[name=goodsname]").val(d.info.goodsname);
                    $("#formpay input[name=istype]").val(d.info.istype);
                    $('#formpay input[name=key]').val(d.info.key);
                    $('#formpay input[name=notify_url]').val(d.info.notify_url);
                    $('#formpay input[name=orderid]').val(d.info.orderid);
                    $('#formpay input[name=orderuid]').val(d.info.orderuid);
                    $('#formpay input[name=price]').val(d.info.price);
                    $('#formpay input[name=return_url]').val(d.info.return_url);
                    $('#formpay input[name=uid]').val(d.info.uid);
                    $('#formpay input[name=formpay_btn]').click();
                } else {
                    $(pay_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(pay_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }

    $('#price_table button[name=alipay_35]').on('click', function() { pay(3.5, 1) });
    $('#price_table button[name=weixin_35]').on('click', function() { pay(3.5, 2) });

    $('#price_table button[name=alipay_65]').on('click', function() { pay(6.5, 1) });
    $('#price_table button[name=weixin_65]').on('click', function() { pay(6.5, 2) });

    $('#price_table button[name=alipay_180]').on('click', function() { pay(18, 1) });
    $('#price_table button[name=weixin_180]').on('click', function() { pay(18, 2) });

    $('#price_table button[name=alipay_1500]').on('click', function() { pay(150, 1) });
    $('#price_table button[name=weixin_1500]').on('click', function() { pay(150, 2) });

    $('#sms_task_modal').on('show.bs.modal', function(event) {
        var modal = $(this);
        var button = $(event.relatedTarget); // Button that triggered the modal
        var action = button.data('action'); // Extract info from data-* attributes

        modal.find('form').trigger('reset');
        modal.find('form span[name=sms_task_form_result]').text('');
        //$('#sms_task_form').trigger('reset');

        load_sms_template_name();
        load_contact_name();
        
        var s_id = '#sms_task_form input[name=id]'
        var s_name = '#sms_task_form input[name=name]'
        var s_content = '#sms_task_form input[name=content]'
        var s_comment = '#sms_task_form input[name=comment]'
        switch (action) {
            case 'create':
                modal.find('#create_sms_task_btn').removeClass('hidden');
                modal.find('#delete_sms_task_btn').addClass('hidden');
                modal.find('#edit_sms_task_btn').addClass('hidden');

                modal.find('.modal-title').text('创建任务');
                break;
            case 'delete':
                modal.find('#create_sms_task_btn').addClass('hidden');
                modal.find('#delete_sms_task_btn').removeClass('hidden');
                modal.find('#edit_sms_task_btn').addClass('hidden');
                modal.find('.modal-title').text('删除任务');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var comment = button.data('comment');

                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', true);
                modal.find(s_content).val(content);
                modal.find(s_content).prop('disabled', true);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', true);
                break;
            case 'edit':
                modal.find('#create_sms_task_btn').addClass('hidden');
                modal.find('#delete_sms_task_btn').addClass('hidden');
                modal.find('#edit_sms_task_btn').removeClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var comment = button.data('comment');

                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_content).val(content);
                modal.find(s_content).prop('disabled', false);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', false);
                break;
            default:
                break;
        }
    });

    var sms_task_btn_handler = function(action) {
        var p = $('#sms_task_form').serialize();
        
        var s_result = '#sms_task_form span[name=sms_task_form_result]';

        $.ajax({  
            type: "post",  
            url: "/sms/task/" + action,  
            data: p,
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在处理</span>");
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $(s_result).html("<span style='color:blue'>处理成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }

    $('#create_sms_task_btn').on('click', function() {
        sms_task_btn_handler('create');
    });

    $('#delete_sms_task_btn').on('click', function() {
        sms_task_btn_handler('delete');
    });

    $('#sms_task_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            fields: {
                name: {
                    validators: {
                        notEmpty: { message: '请输入模板名称' },
                    }
                },
                content: {
                    validators: {
                        notEmpty: { message: '请输入模板内容' },
                    }
                },
                sms_sign_name: {
                    validators: {
                        notEmpty: { message: '请选择一个签名' },
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });

    // 联系人明细------------------------------------------------------------------------------
    $('#contact_user_modal').on('show.bs.modal', function(event) {
        var modal = $(this);
        var button = $(event.relatedTarget); // Button that triggered the modal
        var action = button.data('action'); // Extract info from data-* attributes

        modal.find('form').trigger('reset');
        modal.find('form span[name=contact_user_form_result]').text('');
        //$('#contact_user_form').trigger('reset');

        var s_id = '#contact_user_form input[name=id]'
        var s_contact_id = '#contact_user_form input[name=contact_id]'
        var s_phone = '#contact_user_form input[name=phone]'
        var s_email = '#contact_user_form input[name=email]'
        var s_vars = '#contact_user_form input[name=vars]'
        switch (action) {
            case 'create':
                modal.find('#create_contact_user_btn').removeClass('hidden');
                modal.find('#delete_contact_user_btn').addClass('hidden');
                modal.find('#edit_contact_user_btn').addClass('hidden');

                modal.find('.modal-title').text('创建联系人');
                break;
            case 'delete':
                modal.find('#create_contact_user_btn').addClass('hidden');
                modal.find('#delete_contact_user_btn').removeClass('hidden');
                modal.find('#edit_contact_user_btn').addClass('hidden');
                modal.find('#append_contact_user_btn').addClass('hidden');

                var id = button.data('id');
                var contact_id = button.data('contact_id');
                var phone = button.data('phone');
                var email = button.data('email');
                var vars = JSON.stringify(button.data('vars'));

                modal.find('.modal-title').text('删除联系人');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_contact_id).val(contact_id);
                modal.find(s_contact_id).prop('disabled', false);
                modal.find(s_phone).val(phone);
                modal.find(s_phone).prop('disabled', true);
                modal.find(s_email).val(email);
                modal.find(s_email).prop('disabled', true);
                modal.find(s_vars).val(vars);
                modal.find(s_vars).prop('disabled', true);
                break;
            case 'edit':
                modal.find('#create_contact_user_btn').addClass('hidden');
                modal.find('#delete_contact_user_btn').addClass('hidden');
                modal.find('#edit_contact_user_btn').removeClass('hidden');
                modal.find('#append_contact_user_btn').addClass('hidden');

                var id = button.data('id');
                var contact_id = button.data('contact_id');
                var phone = button.data('phone');
                var email = button.data('email');
                var vars = JSON.stringify(button.data('vars'));

                modal.find('.modal-title').text('编辑联系人');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_contact_id).val(contact_id);
                modal.find(s_contact_id).prop('disabled', false);
                modal.find(s_phone).val(phone);
                modal.find(s_phone).prop('disabled', false);
                modal.find(s_email).val(email);
                modal.find(s_email).prop('disabled', false);
                modal.find(s_vars).val(vars);
                modal.find(s_vars).prop('disabled', false);
                break;
            default:
                break;
        }
    });

    var contact_user_btn_handler = function(action) {
        var p = $('#contact_user_form').serialize();
        
        var form_data = new FormData($('#contact_user_form')[0]);

        var s_result = '#contact_user_form span[name=contact_user_form_result]';
        var s_upload_result = '#contact_user_form span[name=contact_user_form_upload_result]';

        $.ajax({  
            type: "post",  
            url: "/contact_user/" + action,  
            data: p,
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在处理</span>");
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $(s_result).html("<span style='color:blue'>处理成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }

    $('#create_contact_user_btn').on('click', function() {
        contact_user_btn_handler('create');
    });

    $('#delete_contact_user_btn').on('click', function() {
        contact_user_btn_handler('delete');
    });
    
    $('#edit_contact_user_btn').on('click', function() {
        contact_user_btn_handler('edit');
    });

    $('#append_contact_user_btn').on('click', function() {
        contact_user_btn_handler('append');
    });

    $('#contact_user_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            fields: {
                name: {
                    validators: {
                        notEmpty: { message: '请输入模板名称' },
                    }
                },
                content: {
                    validators: {
                        notEmpty: { message: '请输入模板内容' },
                    }
                },
                sms_sign_name: {
                    validators: {
                        notEmpty: { message: '请选择一个签名' },
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });


    //------------------------------------------------------------------------------


    //------------------------------------------------------------------------------
    $('#contact_modal').on('show.bs.modal', function(event) {
        var modal = $(this);
        var button = $(event.relatedTarget); // Button that triggered the modal
        var action = button.data('action'); // Extract info from data-* attributes

        modal.find('form').trigger('reset');
        modal.find('form span[name=contact_form_result]').text('');
        modal.find('form span[name=contact_form_upload_result]').text('');
        //$('#contact_form').trigger('reset');

        var s_id = '#contact_form input[name=id]'
        var s_name = '#contact_form input[name=name]'
        var s_comment = '#contact_form input[name=comment]'
        var s_file_upload = '#contact_form div[name=file_upload]'
        var s_file_upload_info = '#contact_form div[name=file_upload_info]'
        switch (action) {
            case 'create':
                modal.find(s_file_upload).removeClass('hidden');

                modal.find('#create_contact_btn').removeClass('hidden');
                modal.find('#delete_contact_btn').addClass('hidden');
                modal.find('#edit_contact_btn').addClass('hidden');
                modal.find('#append_contact_btn').addClass('hidden');
                modal.find(s_file_upload_info).removeClass('hidden');

                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_comment).prop('disabled', false);
                modal.find(s_file_upload).prop('disabled', false);

                modal.find('.modal-title').text('创建联系人');
                break;
            case 'delete':
                modal.find(s_file_upload).addClass('hidden');
                modal.find(s_file_upload_info).addClass('hidden');

                modal.find('#create_contact_btn').addClass('hidden');
                modal.find('#delete_contact_btn').removeClass('hidden');
                modal.find('#edit_contact_btn').addClass('hidden');
                modal.find('#append_contact_btn').addClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var comment = button.data('comment');

                modal.find('.modal-title').text('删除联系人');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', true);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', true);
                break;
            case 'edit':
                modal.find(s_file_upload).addClass('hidden');
                modal.find(s_file_upload_info).addClass('hidden');

                modal.find('#create_contact_btn').addClass('hidden');
                modal.find('#delete_contact_btn').addClass('hidden');
                modal.find('#edit_contact_btn').removeClass('hidden');
                modal.find('#append_contact_btn').addClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var comment = button.data('comment');

                modal.find('.modal-title').text('编辑联系人');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', false);
                modal.find(s_file_upload).prop('disabled', true);
                break;
            case 'append':
                modal.find(s_file_upload).removeClass('hidden');
                modal.find(s_file_upload_info).removeClass('hidden');

                modal.find('#create_contact_btn').addClass('hidden');
                modal.find('#delete_contact_btn').addClass('hidden');
                modal.find('#edit_contact_btn').addClass('hidden');
                modal.find('#append_contact_btn').removeClass('hidden');
                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var comment = button.data('comment');

                modal.find('.modal-title').text('添加记录');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', true);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', true);
                modal.find(s_file_upload).prop('disabled', false);
                break;
            default:
                break;
        }
    });

    var contact_btn_handler = function(action) {
        var p = $('#contact_form').serialize();
        
        var form_data = new FormData($('#contact_form')[0]);

        var s_result = '#contact_form span[name=contact_form_result]';
        var s_upload_result = '#contact_form span[name=contact_form_upload_result]';

        if (action == 'append') {
            var s_id = '#contact_form input[name=id]'
            form_data.set('id', $(s_id).val());
            $.ajax({  
                type: "post",  
                url: "/contact/append",
                cache: false, 
                async: false,
                processData: false,
                dataType: 'json',
                contentType: false,
                data: form_data,
                beforeSend:function() { 
                    $(s_upload_result).html("<span style='color:blue'>正在上传</span>");
                    return true;
                },
                success: function(d) {  
                    if (d.result) {
                        $(s_upload_result).html("<span style='color:blue'>上传成功</span>");
                        location.reload();
                    } else {
                        $(s_upload_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                    }
                },
                error: function() {
                    $(s_upload_result).html("<span style='color:red'>出错了</span>");
                    return true;
                },
                complete: function() {
                }
            });  
        } else {
            $.ajax({  
                type: "post",  
                url: "/contact/" + action,  
                data: p,
                dataType: 'json',  
                contentType: "application/x-www-form-urlencoded; charset=utf-8",  
                beforeSend:function() { 
                    $(s_result).html("<span style='color:blue'>正在处理</span>");
                    return true;
                },
                success: function(d) {  
                    if (action=='create') {
                        if (d.result) {
                            $(s_result).html("<span style='color:blue'>处理成功</span>");
                            form_data.set('id', d.info.contact.id);
                            $.ajax({  
                                type: "post",  
                                url: "/contact/upload_list",
                                cache: false, 
                                async: false,
                                processData: false,
                                dataType: 'json',
                                contentType: false,
                                data: form_data,
                                beforeSend:function() { 
                                    $(s_upload_result).html("<span style='color:blue'>正在上传</span>");
                                    return true;
                                },
                                success: function(d) {  
                                    if (d.result) {
                                        $(s_upload_result).html("<span style='color:blue'>上传成功</span>");
                                        location.reload();
                                    } else {
                                        $(s_upload_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                                    }
                                },
                                error: function() {
                                    $(s_upload_result).html("<span style='color:red'>出错了</span>");
                                    return true;
                                },
                                complete: function() {
                                }
                            });  
                        } else {
                            $(s_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                        }
                    } else {
                        if (d.result) {
                            $(s_result).html("<span style='color:blue'>处理成功</span>");
                            location.reload();
                        } else {
                            $(s_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                        }
                    } 
                },
                error: function() {
                    $(s_result).html("<span style='color:red'>出错了</span>");
                    return true;
                },
                complete: function() {
                }
            });  
        }
    }

    $('#create_contact_btn').on('click', function() {
        contact_btn_handler('create');
    });

    $('#delete_contact_btn').on('click', function() {
        contact_btn_handler('delete');
    });
    
    $('#edit_contact_btn').on('click', function() {
        contact_btn_handler('edit');
    });

    $('#append_contact_btn').on('click', function() {
        contact_btn_handler('append');
    });

    $('#contact_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            fields: {
                name: {
                    validators: {
                        notEmpty: { message: '请输入模板名称' },
                    }
                },
                content: {
                    validators: {
                        notEmpty: { message: '请输入模板内容' },
                    }
                },
                sms_sign_name: {
                    validators: {
                        notEmpty: { message: '请选择一个签名' },
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });


    //------------------------------------------------------------------------------
    // 加载联系人信息
    var load_contact_name = function() {
        var s = '#sms_task_form select[name=contact_id]';
        var s_result = '#sms_task_form span[name=sms_task_form_result]';

        $.ajax({
            type: "get",  
            url: "/contact/list",
            data: '',
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s).html('<option value="">加载中</option>');
                $(s).selectpicker('refresh');
                return true;
            },
            success: function(d) {  
                if (d.result && d.info && d.info.contacts) {
                    var data = d.info.contacts;
                    var html = '';
                    data.forEach(function (i) {
                        html += "<option value='" + i.id+ "'>" + i.name+ "</option>";
                    });
                    $(s).html(html);
                    $(s).selectpicker('refresh');
                } else {
                    $(s_result).html("<span style='color:red'>联系人加载出错, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>联系人加载出错, 原因: 未知</span>");
                return true;
            },
            complete: function() {
            }
        });
    }

    // 加载模板信息
    var load_sms_template_name = function() {
        var s = '#sms_task_form select[name=sms_template_id]';
        var s_result = '#sms_task_form span[name=sms_task_form_result]';

        $.ajax({
            type: "get",  
            url: "/sms/template/list?verify=2",
            data: '',
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s).html('<option value="">加载中</option>');
                $(s).selectpicker('refresh');
                return true;
            },
            success: function(d) {  
                if (d.result && d.info && d.info.sms_templates) {
                    var data = d.info.sms_templates;
                    var html = '';
                    data.forEach(function (i) {
                        html += "<option value='" + i.id+ "'>" + i.name+ "</option>";
                    });
                    $(s).html(html);
                    $(s).selectpicker('refresh');
                } else {
                    $(s_result).html("<span style='color:red'>短信模板加载出错, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>短信模板加载出错, 原因: 未知</span>");
                return true;
            },
            complete: function() {
            }
        });
    }

    // 加载签名信息
    var load_sms_sign_name = function(id) {
        var s = '#sms_template_form select[name=sms_sign_id]';
        var s_result = '#sms_template_form span[name=sms_template_form_result]';

        url = "/sms/sign/list?verify=2";
        if (id) {
            url += '&id=' + id;
        }
        $.ajax({
            type: "get",  
            url: url,
            data: '',
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s).html('<option value="">加载中</option>');
                $(s).selectpicker('refresh');
                return true;
            },
            success: function(d) {  
                if (d.result && d.info && d.info.sms_signs) {
                    var data = d.info.sms_signs;
                    var html = '';
                    data.forEach(function (i) {
                        html += "<option value='" + i.id+ "'>" + i.name+ "</option>";
                    });
                    $(s).html(html);
                    $(s).selectpicker('refresh');
                } else {
                    $(s_result).html("<span style='color:red'>短信签名加载出错, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>短信签名加载出错, 原因: 未知</span>");
                return true;
            },
            complete: function() {
            }
        });

    }

    $('#sms_template_modal').on('show.bs.modal', function(event) {
        var modal = $(this);
        var button = $(event.relatedTarget); // Button that triggered the modal
        var action = button.data('action'); // Extract info from data-* attributes

        modal.find('form').trigger('reset');
        modal.find('form span[name=sms_template_form_result]').text('');
        //$('#sms_template_form').trigger('reset');

        
        var s_id = '#sms_template_form input[name=id]';
        var s_name = '#sms_template_form input[name=name]';
        var s_content = '#sms_template_form textarea[name=content]';
        var s_content_info = '#sms_template_form div[name=content_info]';
        var s_sms_sign_id = '#sms_template_form select[name=sms_sign_id]';
        var s_comment = '#sms_template_form input[name=comment]';
        switch (action) {
            case 'create':
                load_sms_sign_name();
                modal.find('#create_sms_template_btn').removeClass('hidden');
                modal.find('#delete_sms_template_btn').addClass('hidden');
                modal.find('#edit_sms_template_btn').addClass('hidden');
                modal.find(s_content_info).removeClass('hidden');

                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_content).prop('disabled', false);
                modal.find(s_sms_sign_id).prop('disabled', false);
                modal.find(s_comment).prop('disabled', false);
                break;
            case 'delete':
                modal.find('#create_sms_template_btn').addClass('hidden');
                modal.find('#delete_sms_template_btn').removeClass('hidden');
                modal.find('#edit_sms_template_btn').addClass('hidden');
                modal.find(s_content_info).addClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var sms_sign_id = button.data('sms_sign_id');
                var comment = button.data('comment');

                load_sms_sign_name(sms_sign_id);

                modal.find('.modal-title').text('删除模板');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', true);
                modal.find(s_content).val(content);
                modal.find(s_content).prop('disabled', true);
                modal.find(s_sms_sign_id).prop('disabled', true);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', true);
                break;
            case 'edit':
                modal.find('#create_sms_template_btn').addClass('hidden');
                modal.find('#delete_sms_template_btn').addClass('hidden');
                modal.find('#edit_sms_template_btn').removeClass('hidden');
                modal.find(s_content_info).addClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var content = button.data('content');
                var sms_sign_id = button.data('sms_sign_id');
                var comment = button.data('comment');

                load_sms_sign_name(sms_sign_id);
                modal.find('.modal-title').text('编辑模板');

                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_content).val(content);
                modal.find(s_content).prop('disabled', false);
                modal.find(s_sms_sign_id).prop('disabled', false);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', false);
                break;
            default:
                break;
        }
    });

    var sms_template_btn_handler = function(action) {
        var p = $('#sms_template_form').serialize();
        
        var s_result = '#sms_template_form span[name=sms_template_form_result]';
        $.ajax({  
            type: "post",  
            url: "/sms/template/" + action,  
            data: p,
            dataType: 'html',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在处理</span>");
                return true;
            },
            success: function(d) {  
                var data = JSON.parse(d);
                if (data.result) {
                    $(s_result).html("<span style='color:blue'>处理成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>处理失败, 原因:" + data.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }

    $('#create_sms_template_btn').on('click', function() {
        sms_template_btn_handler('create');
    });

    $('#edit_sms_template_btn').on('click', function() {
        sms_template_btn_handler('edit');
    });

    $('#delete_sms_template_btn').on('click', function() {
        sms_template_btn_handler('delete');
    });

    $('#sms_template_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            fields: {
                name: {
                    validators: {
                        notEmpty: { message: '请输入模板名称' },
                    }
                },
                content: {
                    validators: {
                        notEmpty: { message: '请输入模板内容' },
                    }
                },
                sms_sign_name: {
                    validators: {
                        notEmpty: { message: '请选择一个签名' },
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });

    $('#sms_sign_modal').on('show.bs.modal', function(event) {
        var modal = $(this);
        var button = $(event.relatedTarget); // Button that triggered the modal
        var action = button.data('action'); // Extract info from data-* attributes

        modal.find('form').trigger('reset');
        modal.find('form span[name=sms_sign_form_result]').text('');
        //$('#sms_sign_form').trigger('reset');
        

        var s_id = '#sms_sign_form input[name=id]';
        var s_name = '#sms_sign_form input[name=name]';
        var s_comment = '#sms_sign_form input[name=comment]';
        switch (action) {
            case 'create':
                modal.find('#create_sms_sign_btn').removeClass('hidden');
                modal.find('#delete_sms_sign_btn').addClass('hidden');
                modal.find('#edit_sms_sign_btn').addClass('hidden');

                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_comment).prop('disabled', false);
                break;
            case 'delete':
                modal.find('#create_sms_sign_btn').addClass('hidden');
                modal.find('#delete_sms_sign_btn').removeClass('hidden');
                modal.find('#edit_sms_sign_btn').addClass('hidden');

                var id = button.data('id');
                var name = button.data('name');
                var comment = button.data('comment');

                modal.find('.modal-title').text('删除标签');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', true);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', true);
                break;
            case 'edit':
                modal.find('#create_sms_sign_btn').addClass('hidden');
                modal.find('#delete_sms_sign_btn').addClass('hidden');
                modal.find('#edit_sms_sign_btn').removeClass('hidden');
                var id = button.data('id');
                var name = button.data('name');
                var comment = button.data('comment');

                modal.find('.modal-title').text('编辑标签');
                modal.find(s_id).val(id);
                modal.find(s_id).prop('disabled', false);
                modal.find(s_name).val(name);
                modal.find(s_name).prop('disabled', false);
                modal.find(s_comment).val(comment);
                modal.find(s_comment).prop('disabled', false);
                break;
            default:
                break;
        }
    });
    
    var sms_sign_btn_handler = function(action) {
        var p = $('#sms_sign_form').serialize();
        
        var s_result = '#sms_sign_form span[name=sms_sign_form_result]';
        $.ajax({  
            type: "post",  
            url: "/sms/sign/" + action,  
            data: p,
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在处理</span>");
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $(s_result).html("<span style='color:blue'>处理成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>处理失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    }

    $('#create_sms_sign_btn').on('click', function() {
        sms_sign_btn_handler('create');
    });

    $('#edit_sms_sign_btn').on('click', function() {
        sms_sign_btn_handler('edit');
    });

    $('#delete_sms_sign_btn').on('click', function() {
        sms_sign_btn_handler('delete');
    });

    $('#sms_sign_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: "focus blur",
            fields: {
                name: {
                    validators: {
                        notEmpty: { message: '请输入签名名称' },
                        stringLength: {
                            max: 8,
                            min: 3,
                            message: '签名只允许是3-8个字符'
                        },
                        regexp: { 
                            regexp: /^[a-zA-Z1-9](?=.*?[\u4e00-\u9fa5].*?)[\u4e00-\u9fa5a-zA-Z1-9]+|[\u4e00-\u9fa5][\u4e00-\u9fa5a-zA-Z1-9]+$/,
                            message: '必须含有中文, 在有中文的情况下可以附加英文和数字, 且签名只允许是3-8个字符'
                        },
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });

    $('#login_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            fields: {
                phone: {
                    validators: {
                        notEmpty: { message: '请输入手机号码' }
                    }
                },
                passwd: {
                    validators: {
                        stringLength: {
                            max: 18,
                            min: 6,
                            message: '密码长度需要[6, 18]之间'
                        },
                        notEmpty: { message: '请输入密码' }
                    }
                },
            }
        }).on('status.field.bv', function (e, data) {
            if (data.bv.getSubmitButton()) {
                data.bv.disableSubmitButtons(false);
            }
        });

    $('#login_form button[name=login]').on('click', function() {
        var p = $('#login_form').serialize();
        
        var s_result = '#login_form span[name=login_form_result]';

        $.ajax({  
            type: "post",  
            url: "/login",
            data: p,
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在登录</span>");
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $(s_result).html("<span style='color:blue'>登录成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>登录失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    });

    $('#register_form button[name=register]').on('click', function() {
        var p = $('#register_form').serialize();
        
        var s_result = '#register_form span[name=register_form_result]';

        $.ajax({  
            type: "post",  
            url: "/register",
            data: p,
            dataType: 'json',  
            contentType: "application/x-www-form-urlencoded; charset=utf-8",  
            beforeSend:function() { 
                $(s_result).html("<span style='color:blue'>正在注册</span>");
                return true;
            },
            success: function(d) {  
                if (d.result) {
                    $(s_result).html("<span style='color:blue'>注册成功</span>");
                    location.reload();
                } else {
                    $(s_result).html("<span style='color:red'>注册失败, 原因:" + d.message + "</span>");
                }
            },
            error: function() {
                $(s_result).html("<span style='color:red'>出错了</span>");
                return true;
            },
            complete: function() {
            }
        });  
    });

    $('#register_form').bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            trigger: 'blur',
            //submitButtons: '#register_form button[name="register"]',
            fields: {
                phone: {
                    validators: {
                        phone: {
                            country: 'CN',
                            message: '请输入中国大陆地区的手机号'
                        },
                        notEmpty: { message: '请输入手机号码' }
                    }
                },
                passwd1: {
                    validators: {
                        stringLength: {
                            max: 18,
                            min: 6,
                            message: '密码长度需要[6, 18]之间'
                        },
                        notEmpty: { message: '请输入密码' }
                    }
                },
                passwd2: {
                    validators: {
                        stringLength: {
                            max: 18,
                            min: 6,
                            message: '密码长度需要[6, 18]之间'
                        },
                        notEmpty: { message: '请再次输入密码' },
                        identical: {
                            field: 'passwd1',
                            message: '两次输入密码不相同'
                        }
                    }
                }
            }
        }).on('status.field.bv', function (e, data) {
            // $(e.target)  --> The field element
            // data.bv      --> The BootstrapValidator instance
            // data.field   --> The field name
            // data.element --> The field element

            //if (data.bv.getSubmitButton()) {
            //    data.bv.disableSubmitButtons(false);
            //}
        });
});


